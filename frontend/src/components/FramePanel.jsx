function FramePanel({ frames, currentFrame, onSelect, onAdd }) {
  return (
    <div style={{ display: "flex", gap: "8px", margin: "16px 0" }}>
      {frames.map((_, i) => (
        <button
          key={i}
          onClick={() => onSelect(i)}
          style={{ fontWeight: i === currentFrame ? "bold" : "normal" }}
        >
          フレーム {i + 1}
        </button>
      ))}
      <button onClick={onAdd}>+ 追加</button>
    </div>
  );
}

export default FramePanel;
