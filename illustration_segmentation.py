import cv2
import numpy as np


def segment_by_background_color(image_bytes: bytes, threshold: float = 40.0) -> bytes | None:
    # イラストはMediaPipe Selfie Segmentation（実写真向け）がうまく機能しないため、
    # 背景が単色であることを前提に、背景色との色距離でマスクを作る簡易的な代替手段
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        return None

    border = np.concatenate([image[0, :], image[-1, :], image[:, 0], image[:, -1]])
    background_color = np.median(border, axis=0)

    diff = np.linalg.norm(image.astype(np.float32) - background_color, axis=2)
    mask = (diff > threshold).astype(np.uint8) * 255

    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    success, encoded = cv2.imencode(".png", mask)
    if not success:
        return None

    return encoded.tobytes()
