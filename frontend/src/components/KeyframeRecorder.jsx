import { useState } from "react";

const BONE_NAMES = [
  "head", "neck", "chest", "spine", "hips",
  "leftUpperArm", "leftLowerArm", "leftHand",
  "rightUpperArm", "rightLowerArm", "rightHand",
  "leftUpperLeg", "leftLowerLeg", "leftFoot",
  "rightUpperLeg", "rightLowerLeg", "rightFoot",
];

function capturePose(vrm) {
  const pose = {};
  for (const name of BONE_NAMES) {
    const node = vrm.humanoid?.getNormalizedBoneNode(name);
    if (node) pose[name] = { x: node.rotation.x, y: node.rotation.y, z: node.rotation.z };
  }
  return pose;
}

function applyPose(vrm, pose) {
  for (const name of Object.keys(pose)) {
    const node = vrm.humanoid?.getNormalizedBoneNode(name);
    if (node) node.rotation.set(pose[name].x, pose[name].y, pose[name].z);
  }
}

function lerpPose(a, b, t) {
  const result = {};
  for (const name of Object.keys(a)) {
    result[name] = {
      x: a[name].x + (b[name].x - a[name].x) * t,
      y: a[name].y + (b[name].y - a[name].y) * t,
      z: a[name].z + (b[name].z - a[name].z) * t,
    };
  }
  return result;
}

function KeyframeRecorder({ vrm, canvas }) {
  const [keyframes, setKeyframes] = useState([]);
  const [recording, setRecording] = useState(false);

  const handleAddKeyframe = () => setKeyframes((prev) => [...prev, capturePose(vrm)]);
  const handleClear = () => setKeyframes([]);

  const handleExport = async () => {
    if (!canvas || keyframes.length < 2) return;
    setRecording(true);
    // アニメ的なカクつきを出すため、なめらかに毎フレーム更新せず低いコマ数（10fps）で記録する
    const stream = canvas.captureStream(10);
    const recorder = new MediaRecorder(stream, { mimeType: "video/webm" });
    const chunks = [];
    recorder.ondataavailable = (e) => chunks.push(e.data);
    const stopped = new Promise((resolve) => { recorder.onstop = resolve; });
    recorder.start();

    const stepsPerTransition = 8;
    for (let i = 0; i < keyframes.length - 1; i++) {
      for (let step = 0; step <= stepsPerTransition; step++) {
        applyPose(vrm, lerpPose(keyframes[i], keyframes[i + 1], step / stepsPerTransition));
        await new Promise((r) => setTimeout(r, 150));
      }
    }
    recorder.stop();
    await stopped;

    const blob = new Blob(chunks, { type: "video/webm" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "animation.webm";
    a.click();
    URL.revokeObjectURL(url);
    setRecording(false);
  };

  return (
    <div style={{ padding: "16px" }}>
      <button onClick={handleAddKeyframe} disabled={!vrm}>キーフレームを追加（{keyframes.length}個）</button>
      <button onClick={handleClear} disabled={keyframes.length === 0}>クリア</button>
      <button onClick={handleExport} disabled={keyframes.length < 2 || recording}>
        {recording ? "書き出し中..." : "動画を書き出す"}
      </button>
    </div>
  );
}

export default KeyframeRecorder;
