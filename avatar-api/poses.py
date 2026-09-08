"""撮影プロトコルで使う、固定・既知のポーズ（軸角度θ）を定義する。

シルエットフィッティングは体型(β)とカメラに対する向き（ルート回転）のみを
最適化対象とし、それ以外の関節角度は「撮影時に既知の固定ポーズ」として扱う
（docs/tech/silhouette-fitting-experiment.md参照）。
"""
import torch

LEFT_SHOULDER, RIGHT_SHOULDER = 16, 17


def t_pose() -> torch.Tensor:
    """Tポーズ（全関節角度ゼロ、SMPLのbind poseそのもの）。"""
    return torch.zeros(24, 3)


def arms_down_pose(drop_deg: float) -> torch.Tensor:
    """両腕をTポーズの水平状態から`drop_deg`度だけ下げたポーズ（定数、勾配なし）。"""
    return arms_down_pose_torch(torch.deg2rad(torch.tensor(float(drop_deg))))


def arms_down_pose_torch(angle_rad: torch.Tensor) -> torch.Tensor:
    """`arms_down_pose`の微分可能版。`angle_rad`（スカラーテンソル）まで勾配が流れるため、
    腕を下げた角度自体を目視の固定値ではなく最適化パラメータとして扱える。

    左右の肩関節をZ軸まわりに回転させる。SMPLの骨格は左右鏡映の構造のため、
    同じ角度だけ腕を下げるには左肩と右肩で符号を逆にする必要がある
    （`explore.py`相当の検証で、左肩は負・右肩は正のZ回転で腕が下がることを確認済み）。
    """
    device = angle_rad.device
    zero = torch.zeros((), device=device, dtype=angle_rad.dtype)
    rows = []
    for i in range(24):
        if i == LEFT_SHOULDER:
            rows.append(torch.stack([zero, zero, -angle_rad]))
        elif i == RIGHT_SHOULDER:
            rows.append(torch.stack([zero, zero, angle_rad]))
        else:
            rows.append(torch.zeros(3, device=device, dtype=angle_rad.dtype))
    return torch.stack(rows, dim=0)
