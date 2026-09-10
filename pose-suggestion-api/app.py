"""現在の姿勢＋テキストから、次の姿勢を提案するサービス。

self-model-experimentで検証した次フレーム予測モデル（`frame_transition_model.py`、
`docs/design/motion-generation-from-scratch-handoff.md`参照）を、avatar-api・motion-apiと
同じ構成（FastAPI）でラップする。ユーザーが毎ステップ提案を確認・手直ししながら
キーフレームをつなげてアニメーションを作る運用を想定している（連鎖の自動繰り返しは
ドリフト（誤差蓄積）で崩壊することが分かっているため、あえて1ステップだけ提案する）。
"""
import os

import numpy as np
import torch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from frame_transition_model import FrameTransitionModel
from motion_text_vocab import encode
from rotation_utils import euler_xyz_to_matrix, matrix_to_axis_angle, matrix_to_euler_xyz
from smpl_lbs import axis_angle_to_matrix

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"],
)

CHECKPOINT_PATH = os.environ.get("POSE_SUGGESTION_CHECKPOINT", "frame_transition_model_v2.pt")
MAX_LEN = 8

# self-model-experimentのexport_vrm_pose.py・motion_diffusion_to_vrm_pose.pyの対応表をベースに、
# SMPLの残り関節（9,10,11,13,14）も追加した拡張版。cmu_to_smpl.pyのリターゲティングはSMPLの
# 24関節すべてを埋めているため、モデルの再学習なしにこれらを出力へ含められる
# （22,23=SMPLのhand関節はVRM側に対応するボーンがなく手首と役割が重複するため未使用）
SMPL_TO_VRM = {
    0: "hips", 1: "leftUpperLeg", 2: "rightUpperLeg", 3: "spine",
    4: "leftLowerLeg", 5: "rightLowerLeg", 6: "chest",
    7: "leftFoot", 8: "rightFoot", 9: "upperChest", 10: "leftToes", 11: "rightToes",
    12: "neck", 13: "leftShoulder", 14: "rightShoulder", 15: "head",
    16: "leftUpperArm", 17: "rightUpperArm", 18: "leftLowerArm", 19: "rightLowerArm",
    20: "leftHand", 21: "rightHand",
}
VRM_TO_SMPL = {v: k for k, v in SMPL_TO_VRM.items()}

checkpoint = torch.load(CHECKPOINT_PATH, map_location="cpu", weights_only=False)
model = FrameTransitionModel(vocab_size=len(checkpoint["vocab"]), history=checkpoint["history"])
model.load_state_dict(checkpoint["model_state"])
model.eval()


class BoneRotation(BaseModel):
    x: float
    y: float
    z: float


class SuggestNextPoseRequest(BaseModel):
    current_pose: dict[str, BoneRotation]
    history: list[dict[str, BoneRotation]] = []
    text: str


def vrm_pose_to_smpl(vrm_pose: dict) -> np.ndarray:
    """VRMの姿勢（ボーン名 -> xyz） -> SMPLの24関節軸角度（対応しない関節はゼロのまま）。"""
    smpl_pose = np.zeros((24, 3), dtype=np.float32)
    for bone_name, rot in vrm_pose.items():
        smpl_idx = VRM_TO_SMPL.get(bone_name)
        if smpl_idx is None:
            continue
        matrix = euler_xyz_to_matrix((rot["x"], rot["y"], rot["z"]))
        smpl_pose[smpl_idx] = matrix_to_axis_angle(matrix)
    return smpl_pose


def smpl_to_vrm_pose(smpl_pose: np.ndarray) -> dict:
    """SMPLの24関節軸角度 -> VRMの姿勢（対応する17ボーンのみ）。"""
    matrices = axis_angle_to_matrix(torch.tensor(smpl_pose, dtype=torch.float32)).numpy()
    vrm_pose = {}
    for smpl_idx, bone_name in SMPL_TO_VRM.items():
        x, y, z = matrix_to_euler_xyz(matrices[smpl_idx])
        vrm_pose[bone_name] = {"x": float(x), "y": float(y), "z": float(z)}
    return vrm_pose


def build_window(current: dict, history: list, window_size: int) -> list:
    """(履歴 + 現在)を`window_size`枚に揃える。足りない分は最古のフレームを繰り返して埋める。"""
    combined = history + [current]
    if len(combined) < window_size:
        combined = [combined[0]] * (window_size - len(combined)) + combined
    return combined[-window_size:]


@app.post("/suggest-next-pose")
def suggest_next_pose(req: SuggestNextPoseRequest):
    current_dict = {name: rot.model_dump() for name, rot in req.current_pose.items()}
    history_dicts = [{name: rot.model_dump() for name, rot in h.items()} for h in req.history]

    window = build_window(current_dict, history_dicts, checkpoint["history"])
    window_smpl = np.stack([vrm_pose_to_smpl(pose) for pose in window])  # (history, 24, 3)

    window_t = torch.tensor(window_smpl, dtype=torch.float32).unsqueeze(0)
    window_norm = (window_t.reshape(1, -1) - checkpoint["history_mean"]) / checkpoint["history_std"]
    window_norm = window_norm.reshape(1, checkpoint["history"], 24, 3)

    token_ids = torch.tensor([encode(req.text, checkpoint["vocab"], MAX_LEN)])
    with torch.no_grad():
        pred_norm = model(window_norm, token_ids)
    delta = (pred_norm.reshape(-1) * checkpoint["delta_std"] + checkpoint["delta_mean"]).reshape(24, 3).numpy()

    current_smpl = window_smpl[-1]
    r_cur = axis_angle_to_matrix(torch.tensor(current_smpl, dtype=torch.float32)).numpy()
    r_delta = axis_angle_to_matrix(torch.tensor(delta, dtype=torch.float32)).numpy()
    r_next = r_delta @ r_cur
    next_smpl = np.stack([matrix_to_axis_angle(r_next[j]) for j in range(24)])

    return {"next_pose": smpl_to_vrm_pose(next_smpl)}
