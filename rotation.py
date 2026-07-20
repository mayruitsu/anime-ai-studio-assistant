import math

from body_parts import BODY_PARTS


def _angle_deg(p1: dict, p2: dict) -> float:
    return math.degrees(math.atan2(p2["y"] - p1["y"], p2["x"] - p1["x"]))


def _distance(p1: dict, p2: dict) -> float:
    return math.hypot(p2["x"] - p1["x"], p2["y"] - p1["y"])


def calc_rotation_angles(base_points: list[dict], target_points: list[dict]) -> dict[str, float]:
    angles = {}

    for name, part in BODY_PARTS.items():
        start_idx, end_idx = part["joints"]
        base_angle = _angle_deg(base_points[start_idx], base_points[end_idx])
        target_angle = _angle_deg(target_points[start_idx], target_points[end_idx])
        angles[name] = target_angle - base_angle

    return angles


def calc_scales(base_points: list[dict], target_points: list[dict]) -> dict[str, float]:
    # 肩や股関節をドラッグして関節間の距離が写真と変わった場合、パーツを伸縮させて
    # 隣り合うパーツ（上腕と前腕など）の継ぎ目が離れて「ちぎれて」見えるのを防ぐ
    scales = {}

    for name, part in BODY_PARTS.items():
        start_idx, end_idx = part["joints"]
        base_len = _distance(base_points[start_idx], base_points[end_idx])
        target_len = _distance(target_points[start_idx], target_points[end_idx])
        scales[name] = target_len / base_len if base_len > 1e-6 else 1.0

    return scales
