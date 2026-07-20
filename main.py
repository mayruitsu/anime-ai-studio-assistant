import json

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from pose import detect_pose
from segmentation import segment_person
from video import generate_video

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/detect-pose")
async def detect_pose_endpoint(file: UploadFile = File(...)):
    contents = await file.read()
    landmarks = detect_pose(contents)

    if landmarks is None:
        raise HTTPException(status_code=400, detail="画像の読み込みに失敗しました")

    return {"landmarks": landmarks}


@app.post("/segment-person")
async def segment_person_endpoint(file: UploadFile = File(...)):
    contents = await file.read()
    mask_bytes = segment_person(contents)

    if mask_bytes is None:
        raise HTTPException(status_code=400, detail="画像の読み込みに失敗しました")

    return Response(content=mask_bytes, media_type="image/png")


@app.post("/export-video")
async def export_video(file: UploadFile = File(...), frames: str = Form(...)):
    image_bytes = await file.read()
    frames_data = json.loads(frames)
    video_bytes = generate_video(image_bytes, frames_data)
    return Response(
        content=video_bytes,
        media_type="video/mp4",
        headers={"Content-Disposition": "attachment; filename=animation.mp4"},
    )
