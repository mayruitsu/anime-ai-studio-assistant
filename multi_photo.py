import math

from body_parts import BODY_PARTS
from pose import detect_pose
from segmentation import segment_person
from part_cropping import crop_parts


def _segment_angle(points: list[dict], start_idx: int, end_idx: int) -> float:
    p1, p2 = points[start_idx], points[end_idx]
    return math.degrees(math.atan2(p2["y"] - p1["y"], p2["x"] - p1["x"]))


def _segment_length(points: list[dict], start_idx: int, end_idx: int) -> float:
    p1, p2 = points[start_idx], points[end_idx]
    return math.hypot(p2["x"] - p1["x"], p2["y"] - p1["y"])


def _normalize_deg(diff: float) -> float:
    return ((diff + 180) % 360) - 180


def build_photo_profiles(photos: list[bytes], segment_fn=segment_person) -> list[dict]:
    # 写真ごとにポーズ検出・人物切り抜き・パーツ切り出しを行い、
    # 「その写真ではどのパーツがどんな角度・長さで写っているか」をまとめて持たせる
    # segment_fnを差し替えれば実写真（segment_person）・イラスト（segment_by_background_color）を切り替えられる
    profiles = []
    for image_bytes in photos:
        base_points = detect_pose(image_bytes)
        if not base_points:
            continue
        mask_bytes = segment_fn(image_bytes)
        parts = crop_parts(image_bytes, mask_bytes, base_points)
        profiles.append({"base_points": base_points, "parts": parts})
    return profiles


def select_parts_for_pose(profiles: list[dict], target_points: list[dict]) -> tuple[dict, dict, dict]:
    # パーツごとに、目標ポーズに一番近い角度で写っている写真を選び、
    # その写真からの回転角・伸縮率を計算する
    parts, angles, scales = {}, {}, {}

    for name, part in BODY_PARTS.items():
        start_idx, end_idx = part["joints"]
        target_angle = _segment_angle(target_points, start_idx, end_idx)
        target_len = _segment_length(target_points, start_idx, end_idx)

        best_profile, best_diff = None, None
        for profile in profiles:
            base_angle = _segment_angle(profile["base_points"], start_idx, end_idx)
            diff = abs(_normalize_deg(target_angle - base_angle))
            if best_diff is None or diff < best_diff:
                best_profile, best_diff = profile, diff

        base_points = best_profile["base_points"]
        base_angle = _segment_angle(base_points, start_idx, end_idx)
        base_len = _segment_length(base_points, start_idx, end_idx)

        parts[name] = best_profile["parts"][name]
        angles[name] = _normalize_deg(target_angle - base_angle)
        scales[name] = target_len / base_len if base_len > 1e-6 else 1.0

    return parts, angles, scales
