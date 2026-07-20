import cv2
import numpy as np

from body_parts import BODY_PARTS, DRAW_ORDER


def _rotate_rgba(image: np.ndarray, angle_deg: float, pivot: tuple[float, float]) -> np.ndarray:
    h, w = image.shape[:2]
    matrix = cv2.getRotationMatrix2D(pivot, angle_deg, 1.0)
    return cv2.warpAffine(image, matrix, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))


def _composite(canvas: np.ndarray, part_image: np.ndarray, x: int, y: int) -> None:
    h, w = part_image.shape[:2]
    canvas_h, canvas_w = canvas.shape[:2]
    x2, y2 = min(x + w, canvas_w), min(y + h, canvas_h)
    if x >= canvas_w or y >= canvas_h or x2 <= 0 or y2 <= 0:
        return

    part_region = part_image[max(0, -y):y2 - y, max(0, -x):x2 - x]
    canvas_region = canvas[max(0, y):y2, max(0, x):x2]
    alpha = part_region[:, :, 3:4].astype(np.float32) / 255.0
    canvas_region[:, :, :3] = (
        part_region[:, :, :3] * alpha + canvas_region[:, :, :3] * (1 - alpha)
    ).astype(np.uint8)


def render_frame(
    parts: dict, angles: dict, target_points: list[dict],
    canvas_size: tuple[int, int], background_color: tuple[int, int, int] | None = (255, 255, 255),
) -> np.ndarray:
    width, height = canvas_size
    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    if background_color is not None:
        canvas[:, :] = background_color

    for name in DRAW_ORDER:
        part = parts.get(name)
        if part is None:
            continue
        pivot_idx = BODY_PARTS[name]["pivot"]
        target_x = target_points[pivot_idx]["x"] * width
        target_y = target_points[pivot_idx]["y"] * height
        rotated = _rotate_rgba(part["image"], angles[name], part["pivot_offset"])
        paste_x = int(target_x - part["pivot_offset"][0])
        paste_y = int(target_y - part["pivot_offset"][1])
        _composite(canvas, rotated, paste_x, paste_y)

    return canvas
