import cv2
import numpy as np

from body_parts import BODY_PARTS


def _landmark_px(landmark: dict, width: int, height: int) -> np.ndarray:
    return np.array([landmark["x"] * width, landmark["y"] * height])


def crop_parts(image_bytes: bytes, mask_bytes: bytes, landmarks: list[dict], margin_ratio: float = 0.3) -> dict:
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    mask_nparr = np.frombuffer(mask_bytes, np.uint8)
    mask = cv2.imdecode(mask_nparr, cv2.IMREAD_GRAYSCALE)

    height, width = image.shape[:2]
    parts = {}

    for name, part in BODY_PARTS.items():
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
        b, g, r = cv2.split(cropped_image)
        rgba = cv2.merge([b, g, r, cropped_mask])

        pivot_px = _landmark_px(landmarks[part["pivot"]], width, height)

        parts[name] = {
            "image": rgba,
            "bbox": (x1, y1, x2, y2),
            "pivot_offset": (pivot_px[0] - x1, pivot_px[1] - y1),
        }

    return parts
