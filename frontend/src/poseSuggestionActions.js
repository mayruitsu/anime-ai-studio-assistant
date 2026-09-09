import { capturePose } from "./vrmPose";

export async function suggestNextPose(vrm, history, text) {
  const currentPose = capturePose(vrm);
  const res = await fetch("http://localhost:8093/suggest-next-pose", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ current_pose: currentPose, history, text }),
  });
  const data = await res.json();
  return { currentPose, nextPose: data.next_pose };
}
