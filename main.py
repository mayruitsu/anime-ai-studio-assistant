from fastapi import FastAPI, File, HTTPException, UploadFile

from pose import detect_pose

app = FastAPI()


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
