import asyncio
import json
import uuid

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from pose import detect_pose
from segmentation import segment_person
from video import generate_video

app = FastAPI()

# 会話アシスタントからのツール呼び出しをブラウザへ中継するための状態。
# ブラウザ側がVRMの実体を持つため、ツールの実行自体は常にブラウザで行う。
_browser_connections: dict[str, WebSocket] = {}
_pending_tool_calls: dict[str, asyncio.Future] = {}

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


@app.websocket("/ws/tools")
async def tools_websocket(websocket: WebSocket):
    """ブラウザ（VRMの実体を持つ側）が接続し、ツール呼び出しを受け取って結果を返す。"""
    await websocket.accept()
    connection_id = str(uuid.uuid4())
    _browser_connections[connection_id] = websocket
    try:
        while True:
            message = await websocket.receive_json()
            if message.get("type") == "tool_result":
                future = _pending_tool_calls.pop(message["id"], None)
                if future and not future.done():
                    future.set_result(message.get("result"))
    except WebSocketDisconnect:
        _browser_connections.pop(connection_id, None)


@app.post("/tools/call")
async def call_tool(payload: dict):
    """会話アシスタント等から、ブラウザ側のツールを呼び出すためのエンドポイント。"""
    if not _browser_connections:
        raise HTTPException(status_code=503, detail="ブラウザが接続されていません")

    tool = payload.get("tool")
    params = payload.get("params", {})
    call_id = str(uuid.uuid4())
    websocket = next(iter(_browser_connections.values()))

    future = asyncio.get_event_loop().create_future()
    _pending_tool_calls[call_id] = future
    await websocket.send_json({"type": "tool_call", "id": call_id, "tool": tool, "params": params})

    try:
        # export_keyframe_videoなど、実行に時間がかかるツールも考慮した猶予
        result = await asyncio.wait_for(future, timeout=60.0)
    except asyncio.TimeoutError:
        _pending_tool_calls.pop(call_id, None)
        raise HTTPException(status_code=504, detail="ツール呼び出しがタイムアウトしました")

    return {"result": result}


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
