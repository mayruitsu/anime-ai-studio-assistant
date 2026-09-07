import { capturePose } from "./vrmPose";

// VRMの実体はブラウザ側にしかないため、会話アシスタントからの操作は
// すべてここに登録されたツール関数を通じて実行する。
export function createToolRegistry(getVrm) {
  return {
    get_current_pose: () => capturePose(getVrm()),
    set_bone_rotation: ({ bone_name, x, y, z }) => {
      const vrm = getVrm();
      const node = vrm?.humanoid?.getNormalizedBoneNode(bone_name);
      if (!node) return { error: `unknown bone: ${bone_name}` };
      node.rotation.set(x, y, z);
      return { ok: true };
    },
  };
}

export function connectToolBridge(url, tools) {
  const ws = new WebSocket(url);
  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.type !== "tool_call") return;
    const handler = tools[message.tool];
    const result = handler ? handler(message.params) : { error: `unknown tool: ${message.tool}` };
    ws.send(JSON.stringify({ type: "tool_result", id: message.id, result }));
  };
  return ws;
}
