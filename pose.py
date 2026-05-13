import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose


def detect_pose(image_bytes: bytes) -> list[dict] | None:
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        return None

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(image_rgb)

    if not results.pose_landmarks:
        return []

    return [
        {
            "index": i,
            "x": lm.x,
            "y": lm.y,
            "z": lm.z,
            "visibility": lm.visibility,
        }
        for i, lm in enumerate(results.pose_landmarks.landmark)
    ]
