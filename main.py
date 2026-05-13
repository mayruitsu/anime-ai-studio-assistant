import cv2
import mediapipe as mp
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile

app = FastAPI()
mp_pose = mp.solutions.pose


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/detect-pose")
async def detect_pose(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(status_code=400, detail="画像の読み込みに失敗しました")

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(image_rgb)

    if not results.pose_landmarks:
        return {"landmarks": []}

    landmarks = [
        {
            "index": i,
            "x": lm.x,
            "y": lm.y,
            "z": lm.z,
            "visibility": lm.visibility,
        }
        for i, lm in enumerate(results.pose_landmarks.landmark)
    ]

    return {"landmarks": landmarks}
