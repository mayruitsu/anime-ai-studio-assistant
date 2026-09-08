"""nvdiffrastを使い、指定した視点からSMPLメッシュのシルエットをレンダリングする。

学習済みAIモデルには依存しない、純粋なラスタライズ処理（射影幾何）。
"""
import numpy as np
import torch


def look_at_orthographic(angle_deg: float, center: torch.Tensor, distance: float, extent: float) -> torch.Tensor:
    """Y軸まわりの角度から、正射影のworld->clip変換行列(4,4)を作る。"""
    center = center.detach().cpu()
    angle = np.radians(angle_deg)
    eye = center + distance * torch.tensor([np.sin(angle), 0.0, np.cos(angle)], dtype=torch.float32)
    forward = torch.nn.functional.normalize(center - eye, dim=0)
    up_hint = torch.tensor([0.0, 1.0, 0.0])
    right = torch.nn.functional.normalize(torch.linalg.cross(forward, up_hint), dim=0)
    up = torch.linalg.cross(right, forward)

    view = torch.eye(4)
    view[0, :3] = right
    view[1, :3] = up
    view[2, :3] = -forward
    view[:3, 3] = -view[:3, :3] @ eye

    ortho = torch.eye(4)
    ortho[0, 0] = 1.0 / extent
    ortho[1, 1] = 1.0 / extent
    ortho[2, 2] = -1.0 / (extent * 4)  # near/farを十分広く取った簡易奥行きスケール
    return ortho @ view


def render_silhouette(glctx, vertices: torch.Tensor, faces: torch.Tensor, mvp: torch.Tensor, resolution: int):
    """メッシュを指定のMVP行列でラスタライズし、シルエット(0〜1の連続値)を返す。"""
    import nvdiffrast.torch as dr

    verts_h = torch.cat([vertices, torch.ones(vertices.shape[0], 1, device=vertices.device)], dim=1)
    clip_pos = (mvp.to(vertices.device) @ verts_h.T).T.unsqueeze(0).contiguous()  # (1, V, 4)
    triangles = faces.to(torch.int32).contiguous()
    rast, _ = dr.rasterize(glctx, clip_pos, triangles, resolution=[resolution, resolution])
    coverage = torch.clamp(rast[..., 3:4], 0, 1)  # 三角形に覆われていれば1、背景は0 (1,H,W,1)
    # dr.rasterize()の出力（三角形ID）はエッジで不連続なため勾配がほぼゼロになる。
    # dr.antialias()でシルエットの輪郭を滑らかにし、頂点位置まで勾配が流れるようにする
    coverage = dr.antialias(coverage, rast, clip_pos, triangles)
    # nvdiffrastのラスタライズ結果は行0がクリップ空間のY-（下）に対応するため、
    # 一般的な画像形式（行0が上）に合わせて上下反転する
    return torch.flip(coverage[0, ..., 0], dims=[0])
