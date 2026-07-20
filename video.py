import os
import tempfile

import cv2
import numpy as np

from segmentation import segment_person
from part_cropping import crop_parts
from rotation import calc_rotation_angles
from render import render_frame


def generate_video(image_bytes: bytes, frames: list[list[dict]], fps: int = 2) -> bytes:
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    h, w = image.shape[:2]

    base_points = frames[0]
    mask_bytes = segment_person(image_bytes)
    parts = crop_parts(image_bytes, mask_bytes, base_points)

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        tmp_path = f.name

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(tmp_path, fourcc, fps, (w, h))

    for target_points in frames:
        angles = calc_rotation_angles(base_points, target_points)
        frame = render_frame(parts, angles, target_points, (w, h))
        out.write(frame)

    out.release()

    with open(tmp_path, "rb") as f:
        video_bytes = f.read()
    os.unlink(tmp_path)

    return video_bytes
