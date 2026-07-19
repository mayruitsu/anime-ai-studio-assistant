import os
import tempfile

import cv2
import numpy as np


def generate_video(image_bytes: bytes, frames: list[list[dict]], fps: int = 2) -> bytes:
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    h, w = image.shape[:2]

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        tmp_path = f.name

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(tmp_path, fourcc, fps, (w, h))

    for frame_points in frames:
        frame = image.copy()
        for point in frame_points:
            px = int(point["x"] * w)
            py = int(point["y"] * h)
            cv2.circle(frame, (px, py), 6, (0, 0, 255), -1)
        out.write(frame)

    out.release()

    with open(tmp_path, "rb") as f:
        video_bytes = f.read()
    os.unlink(tmp_path)

    return video_bytes
