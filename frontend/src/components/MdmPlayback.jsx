import { useState } from "react";

function applyPose(vrm, pose) {
  for (const name of Object.keys(pose)) {
    const node = vrm.humanoid?.getNormalizedBoneNode(name);
    if (node) node.rotation.set(pose[name].x, pose[name].y, pose[name].z);
  }
}

function MdmPlayback({ vrm, canvas }) {
  const [frames, setFrames] = useState(null);
  const [text, setText] = useState("");
  const [playing, setPlaying] = useState(false);

  const handleSelectFile = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const data = JSON.parse(await file.text());
    setFrames(data.frames);
    setText(data.text);
  };

  const handlePlay = async () => {
    if (!canvas || !frames) return;
    setPlaying(true);

    const stream = canvas.captureStream(10);
    const recorder = new MediaRecorder(stream, { mimeType: "video/webm" });
    const chunks = [];
    recorder.ondataavailable = (e) => chunks.push(e.data);
    const stopped = new Promise((resolve) => { recorder.onstop = resolve; });
    recorder.start();

    // 20fpsで生成されたMDMのモーションを、アニメ的な間引きのため3フレームに1回だけ反映する
    for (let i = 0; i < frames.length; i += 3) {
      applyPose(vrm, frames[i]);
      await new Promise((r) => setTimeout(r, 100));
    }

    recorder.stop();
    await stopped;

    const blob = new Blob(chunks, { type: "video/webm" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "mdm_animation.webm";
    a.click();
    URL.revokeObjectURL(url);
    setPlaying(false);
  };

  return (
    <div style={{ padding: "16px" }}>
      <h3>AI生成モーション再生（実験）</h3>
      <input type="file" accept=".json" onChange={handleSelectFile} />
      {text && <p>プロンプト: {text}（{frames.length}フレーム）</p>}
      <button onClick={handlePlay} disabled={!vrm || !frames || playing}>
        {playing ? "再生・書き出し中..." : "再生して動画を書き出す"}
      </button>
    </div>
  );
}

export default MdmPlayback;
