import json
import os
import subprocess
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MDM_DIR = os.environ.get("MDM_DIR", "/workspace/mdm")
MODEL_PATH = os.environ.get(
    "MDM_MODEL_PATH", f"{MDM_DIR}/save/humanml_enc_512_50steps/model000750000.pt"
)
EXPORT_SCRIPT = "/app/export_vrm_pose.py"


class GenerateRequest(BaseModel):
    text: str


@app.post("/generate-motion")
def generate_motion(req: GenerateRequest):
    run_id = uuid.uuid4().hex
    out_dir = f"/tmp/mdm_out_{run_id}"

    # generate.pyはモーション生成後、プレビュー動画の描画（moviepy）で失敗して
    # 非0終了することがあるが、その時点でresults.npy自体は保存済みのため無視してよい
    subprocess.run(
        [
            "python", "-m", "sample.generate",
            "--model_path", MODEL_PATH,
            "--text_prompt", req.text,
            "--num_samples", "1",
            "--num_repetitions", "1",
            "--output_dir", out_dir,
        ],
        cwd=MDM_DIR, capture_output=True,
    )
    if not os.path.exists(f"{out_dir}/results.npy"):
        raise HTTPException(status_code=500, detail="モーション生成に失敗しました")

    # render_mesh.pyはファイル名からサンプル番号を読み取るだけなので、中身は空でよい
    dummy_mp4 = f"{out_dir}/sample0_rep0.mp4"
    open(dummy_mp4, "a").close()

    subprocess.run(
        ["python", "-m", "visualize.render_mesh", "--input_path", dummy_mp4],
        cwd=MDM_DIR, check=True, capture_output=True,
    )

    smpl_params_path = f"{out_dir}/sample0_rep0_smpl_params.npy"
    pose_json_path = f"{out_dir}/pose.json"
    env = {**os.environ, "PYTHONPATH": MDM_DIR}
    subprocess.run(
        ["python", EXPORT_SCRIPT, smpl_params_path, pose_json_path],
        cwd=MDM_DIR, env=env, check=True, capture_output=True,
    )

    with open(pose_json_path) as f:
        return json.load(f)
