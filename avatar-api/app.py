"""写真からシルエット抽出→SMPLフィッティング→VRMエクスポートまでを行うサービス。

self-model-experimentリポジトリで検証済みのパイプラインを、motion-apiと同じ
構成（FastAPI、同期エンドポイント、非同期ジョブ管理はフロントエンド側）で提供する。
nvdiffrast（GPU・CUDAコンパイラが必要）に依存するため、現時点ではDocker化せず
WSL2のGPU環境で直接動かす前提（Docker化はmotion-apiより難易度が高いため今後の課題）。
"""
import os
import tempfile

import cv2
import numpy as np
import torch
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from export_vrm import export_vrm
from extract_silhouette import extract_silhouette_gradient
from fit_silhouette import fit_betas_and_root, render_views
from poses import arms_down_pose
from silhouette_alignment import align_mask_to_canvas, mask_bbox_rows
from smpl_model import SmplModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"],
)

SMPL_MODEL_PATH = os.environ["AVATAR_API_SMPL_MODEL_PATH"]
RESOLUTION, DISTANCE, EXTENT = 256, 3.0, 1.2


def fit_avatar_from_photos(front_bytes, back_bytes, side_bytes, side_is_right, arms_drop_deg) -> bytes:
    import nvdiffrast.torch as dr

    device = "cuda"
    model = SmplModel(SMPL_MODEL_PATH)
    for name in ("v_template", "shapedirs", "posedirs", "weights", "faces", "joint_regressor"):
        setattr(model, name, getattr(model, name).to(device))
    kintree_parents = model.kintree_table[0].astype(int).tolist()
    kintree_parents[0] = 0
    center = model.v_template.mean(dim=0)
    glctx = dr.RasterizeCudaContext()
    base_pose = arms_down_pose(arms_drop_deg).to(device)

    ref = render_views(glctx, model, torch.zeros(10, device=device), torch.zeros(3, device=device),
                        kintree_parents, center, RESOLUTION, DISTANCE, EXTENT, base_pose=base_pose)
    top, bottom = mask_bbox_rows(ref[0].detach().cpu().numpy())
    top_frac, bottom_frac = top / RESOLUTION, bottom / RESOLUTION

    def to_target(image_bytes):
        raw = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        mask = extract_silhouette_gradient(raw)
        aligned = align_mask_to_canvas(mask, top_frac, bottom_frac, RESOLUTION)
        return torch.tensor(aligned, dtype=torch.float32, device=device)

    front, back, side = to_target(front_bytes), to_target(back_bytes), to_target(side_bytes)
    side_mirrored = torch.flip(side, dims=[1])
    targets = [front, side_mirrored, back, side] if side_is_right else [front, side, back, side_mirrored]

    betas_hat, _, _, _ = fit_betas_and_root(
        glctx, model, targets, kintree_parents, center, RESOLUTION, DISTANCE, EXTENT,
        num_steps=400, lr=0.03, beta_reg_weight=0.001, init_shoulder_deg=arms_drop_deg,
    )

    with tempfile.NamedTemporaryFile(suffix=".vrm", delete=False) as f:
        export_vrm(model, betas_hat, f.name)
        vrm_path = f.name
    with open(vrm_path, "rb") as f:
        data = f.read()
    os.remove(vrm_path)
    return data


@app.post("/fit-avatar")
def fit_avatar(front: UploadFile = File(...), back: UploadFile = File(...), side: UploadFile = File(...),
               side_is_right: bool = Form(False), arms_drop_deg: float = Form(63.0)):
    vrm_bytes = fit_avatar_from_photos(front.file.read(), back.file.read(), side.file.read(),
                                        side_is_right, arms_drop_deg)
    return Response(content=vrm_bytes, media_type="application/octet-stream")
