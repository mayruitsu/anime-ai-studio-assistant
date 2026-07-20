import cv2
import mediapipe as mp
import numpy as np

mp_selfie_segmentation = mp.solutions.selfie_segmentation


def segment_person(image_bytes: bytes) -> bytes | None:
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        return None

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp_selfie_segmentation.SelfieSegmentation(model_selection=0) as segmenter:
        results = segmenter.process(image_rgb)

    mask = (results.segmentation_mask > 0.5).astype(np.uint8) * 255
    success, encoded = cv2.imencode(".png", mask)

    if not success:
        return None

    return encoded.tobytes()