import math

from body_parts import BODY_PARTS


def _angle_deg(p1: dict, p2: dict) -> float:
    return math.degrees(math.atan2(p2["y"] - p1["y"], p2["x"] - p1["x"]))


def calc_rotation_angles(base_points: list[dict], target_points: list[dict]) -> dict[str, float]:
    angles = {}

    for name, part in BODY_PARTS.items():
        start_idx, end_idx = part["joints"]
        base_angle = _angle_deg(base_points[start_idx], base_points[end_idx])
        target_angle = _angle_deg(target_points[start_idx], target_points[end_idx])
        angles[name] = target_angle - base_angle

    return angles
