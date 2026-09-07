function KeyframeRecorder({ vrm, keyframes, recording, onAddKeyframe, onClear, onExport }) {
  return (
    <div style={{ padding: "16px" }}>
      <button onClick={onAddKeyframe} disabled={!vrm}>キーフレームを追加（{keyframes.length}個）</button>
      <button onClick={onClear} disabled={keyframes.length === 0}>クリア</button>
      <button onClick={onExport} disabled={keyframes.length < 2 || recording}>
        {recording ? "書き出し中..." : "動画を書き出す"}
      </button>
    </div>
  );
}

export default KeyframeRecorder;
