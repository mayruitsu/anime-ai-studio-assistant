import { capturePose } from "./vrmPose";

// VRMの実体はブラウザ側にしかないため、会話アシスタントからの操作は
// すべてここに登録されたツール関数を通じて実行する。
export function createToolRegistry(getVrm, actions = {}) {
  return {
    get_current_pose: () => capturePose(getVrm()),
    set_bone_rotation: ({ bone_name, x, y, z }) => {
      const vrm = getVrm();
      const node = vrm?.humanoid?.getNormalizedBoneNode(bone_name);
      if (!node) return { error: `unknown bone: ${bone_name}` };
      node.rotation.set(x, y, z);
      return { ok: true };
    },
    add_keyframe: () => { actions.addKeyframe?.(); return { ok: true }; },
    clear_keyframes: () => { actions.clearKeyframes?.(); return { ok: true }; },
    export_keyframe_video: async () => { await actions.exportKeyframeVideo?.(); return { ok: true }; },
    load_vrm_model: ({ url }) => {
      if (!url) return { error: "url is required" };
      actions.loadVrmModel?.(url);
      return { ok: true };
    },
    // MDMでのモーション生成は2〜3分かかるため、開始と状態確認を分けた非同期ジョブ方式にする
    start_motion_generation: ({ prompt }) => {
      if (!prompt) return { error: "prompt is required" };
      return { job_id: actions.startMotionGeneration?.(prompt) };
    },
    get_motion_generation_status: ({ job_id }) => actions.getMotionGenerationStatus?.(job_id) ?? { status: "not_found" },
    play_and_export_generated_motion: async ({ job_id }) => {
      const ok = await actions.playAndExportGeneratedMotion?.(job_id);
      return ok ? { ok: true } : { error: "motion not ready" };
    },
  };
}

export function connectToolBridge(url, tools) {
  const ws = new WebSocket(url);
  ws.onmessage = async (event) => {
    const message = JSON.parse(event.data);
    if (message.type !== "tool_call") return;
    const handler = tools[message.tool];
    const result = handler ? await handler(message.params) : { error: `unknown tool: ${message.tool}` };
    ws.send(JSON.stringify({ type: "tool_result", id: message.id, result }));
  };
  return ws;
}
