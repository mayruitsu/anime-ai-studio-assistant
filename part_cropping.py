import cv2
import numpy as np

from body_parts import BODY_PARTS


def _landmark_px(landmark: dict, width: int, height: int) -> np.ndarray:
    return np.array([landmark["x"] * width, landmark["y"] * height])


def _segment_distance_map(width: int, height: int, p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
    ys, xs = np.mgrid[0:height, 0:width]
    seg = p2 - p1
    seg_len_sq = float(np.dot(seg, seg))
    if seg_len_sq < 1e-6:
        return np.hypot(xs - p1[0], ys - p1[1])
    t = np.clip(((xs - p1[0]) * seg[0] + (ys - p1[1]) * seg[1]) / seg_len_sq, 0, 1)
    proj_x, proj_y = p1[0] + t * seg[0], p1[1] + t * seg[1]
    return np.hypot(xs - proj_x, ys - proj_y)


def _build_part_labels(landmarks: list[dict], width: int, height: int) -> tuple[np.ndarray, list[str]]:
    # 画像全体で、各ピクセルがどのパーツの骨（関節を結ぶ線分）に一番近いかを求める。
    # これにより、パーツ同士の矩形が重なっていても他パーツのピクセルが混ざらないようにする
    names = list(BODY_PARTS.keys())
    distances = np.stack([
        _segment_distance_map(
            width, height,
            _landmark_px(landmarks[BODY_PARTS[name]["joints"][0]], width, height),
            _landmark_px(landmarks[BODY_PARTS[name]["joints"][1]], width, height),
        )
        for name in names
    ])
    return np.argmin(distances, axis=0), names


def crop_parts(image_bytes: bytes, mask_bytes: bytes, landmarks: list[dict], margin_ratio: float = 0.3) -> dict:
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    mask_nparr = np.frombuffer(mask_bytes, np.uint8)
    mask = cv2.imdecode(mask_nparr, cv2.IMREAD_GRAYSCALE)

    height, width = image.shape[:2]
    labels, names = _build_part_labels(landmarks, width, height)
    parts = {}

    for i, name in enumerate(names):
        part = BODY_PARTS[name]
        start_idx, end_idx = part["joints"]
        p1 = _landmark_px(landmarks[start_idx], width, height)
        p2 = _landmark_px(landmarks[end_idx], width, height)

        limb_length = np.linalg.norm(p2 - p1)
        margin = max(limb_length * margin_ratio, 10)

        x1 = int(max(min(p1[0], p2[0]) - margin, 0))
        y1 = int(max(min(p1[1], p2[1]) - margin, 0))
        x2 = int(min(max(p1[0], p2[0]) + margin, width))
        y2 = int(min(max(p1[1], p2[1]) + margin, height))

        cropped_image = image[y1:y2, x1:x2]
        cropped_mask = mask[y1:y2, x1:x2]
        own_label_mask = (labels[y1:y2, x1:x2] == i).astype(np.uint8) * 255
        combined_mask = cv2.bitwise_and(cropped_mask, own_label_mask)

        b, g, r = cv2.split(cropped_image)
        rgba = cv2.merge([b, g, r, combined_mask])

        pivot_px = _landmark_px(landmarks[part["pivot"]], width, height)

        parts[name] = {
            "image": rgba,
            "bbox": (x1, y1, x2, y2),
            "pivot_offset": (pivot_px[0] - x1, pivot_px[1] - y1),
        }

    return parts
