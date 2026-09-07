import { applyPose } from "./vrmPose";

export async function generateMotionFromText(prompt) {
  const res = await fetch("http://localhost:8090/generate-motion", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: prompt }),
  });
  return res.json();
}

export async function playAndExportMotion(vrm, canvas, frames) {
  if (!canvas || !frames) return;
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
}
