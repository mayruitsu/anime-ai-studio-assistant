"""SMPLのポーズ変形（Linear Blend Skinning）。

体型変形済みメッシュ(v_shaped)と姿勢パラメータ(θ、24関節×軸角度3次元)から、
実際にポーズしたメッシュ頂点を計算する。すべてPyTorchの演算のみで構成されており、
勾配がβ・θまで流れる（後段のシルエットフィッティングでの最適化に使う）。
"""
import torch


def axis_angle_to_matrix(axis_angle: torch.Tensor) -> torch.Tensor:
    """軸角度表現 (..., 3) を回転行列 (..., 3, 3) に変換する（ロドリゲスの回転公式）。"""
    angle = torch.norm(axis_angle, dim=-1, keepdim=True)
    axis = axis_angle / torch.clamp(angle, min=1e-8)
    angle = angle.unsqueeze(-1)
    x, y, z = axis[..., 0], axis[..., 1], axis[..., 2]
    zeros = torch.zeros_like(x)
    K = torch.stack([
        torch.stack([zeros, -z, y], dim=-1),
        torch.stack([z, zeros, -x], dim=-1),
        torch.stack([-y, x, zeros], dim=-1),
    ], dim=-2)
    eye = torch.eye(3, device=axis_angle.device, dtype=axis_angle.dtype).expand(*axis_angle.shape[:-1], 3, 3)
    return eye + torch.sin(angle) * K + (1 - torch.cos(angle)) * (K @ K)


def forward_kinematics(joints: torch.Tensor, rotations: torch.Tensor, kintree_parents) -> torch.Tensor:
    """各関節のグローバル変換行列(24, 4, 4)を、親子関係をたどって計算する。"""
    num_joints = joints.shape[0]
    local = torch.zeros(num_joints, 4, 4, device=joints.device, dtype=joints.dtype)
    local[:, 3, 3] = 1.0
    local[:, :3, :3] = rotations
    local[0, :3, 3] = joints[0]
    for k in range(1, num_joints):
        local[k, :3, 3] = joints[k] - joints[kintree_parents[k]]

    global_transforms = [local[0]]
    for k in range(1, num_joints):
        global_transforms.append(global_transforms[kintree_parents[k]] @ local[k])
    return torch.stack(global_transforms, dim=0)


def pose_and_skin(v_shaped, joints, pose_axis_angle, posedirs, weights, kintree_parents):
    """体型変形済みメッシュ(v_shaped)を、姿勢パラメータ(24関節分の軸角度)でポーズさせる。"""
    rotations = axis_angle_to_matrix(pose_axis_angle)  # (24, 3, 3)

    # 姿勢依存ブレンドシェイプ：ルート以外の23関節の(R - I)を使う
    eye = torch.eye(3, device=v_shaped.device, dtype=v_shaped.dtype)
    pose_feature = (rotations[1:] - eye).reshape(-1)  # (207,)
    v_posed = v_shaped + torch.einsum("vcd,d->vc", posedirs, pose_feature)

    global_transforms = forward_kinematics(joints, rotations, kintree_parents)  # (24, 4, 4)

    # スキニング用に、レスト位置での関節オフセット分を打ち消した変換に直す
    # (G_k @ [I | -J_k] を、同次座標w=0のJ_kとの積でR_k@J_k部分だけ取り出して計算)
    joints_h = torch.cat([joints, torch.zeros(joints.shape[0], 1, device=joints.device, dtype=joints.dtype)], dim=1)
    rotated_joints = torch.einsum("kij,kj->ki", global_transforms, joints_h)
    skinning_transforms = global_transforms.clone()
    skinning_transforms[:, :3, 3] -= rotated_joints[:, :3]

    v_posed_h = torch.cat([v_posed, torch.ones(v_posed.shape[0], 1, device=v_posed.device, dtype=v_posed.dtype)], dim=1)
    per_vertex_transform = torch.einsum("vk,kij->vij", weights, skinning_transforms)  # (6890, 4, 4)
    v_final_h = torch.einsum("vij,vj->vi", per_vertex_transform, v_posed_h)
    return v_final_h[:, :3]
