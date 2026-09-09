import { useState } from "react";
import { generateMotionFromText, playMotion, playAndExportMotion } from "../motionActions";

function MdmPlayback({ vrm, canvas }) {
  const [frames, setFrames] = useState(null);
  const [text, setText] = useState("");
  const [prompt, setPrompt] = useState("");
  const [generating, setGenerating] = useState(false);
  const [playing, setPlaying] = useState(false);

  const handleSelectFile = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const data = JSON.parse(await file.text());
    setFrames(data.frames);
    setText(data.text);
  };

  const handleGenerate = async () => {
    if (!prompt) return;
    setGenerating(true);
    try {
      const data = await generateMotionFromText(prompt);
      setFrames(data.frames);
      setText(data.text);
    } finally {
      setGenerating(false);
    }
  };

  const handlePlay = async () => {
    setPlaying(true);
    await playMotion(vrm, frames);
    setPlaying(false);
  };

  const handleExport = async () => {
    setPlaying(true);
    await playAndExportMotion(vrm, canvas, frames);
    setPlaying(false);
  };

  return (
    <div style={{ padding: "16px" }}>
      <h3>AI生成モーション再生（実験）</h3>
      <div>
        <input
          type="text"
          placeholder="例：a person jumps up and down happily"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
        <button onClick={handleGenerate} disabled={!prompt || generating}>
          {generating ? "生成中...（2〜3分ほどかかります）" : "AIで生成"}
        </button>
      </div>
      <p>または、生成済みのJSONファイルを選択：</p>
      <input type="file" accept=".json" onChange={handleSelectFile} />
      {text && <p>プロンプト: {text}（{frames.length}フレーム）</p>}
      <button onClick={handlePlay} disabled={!vrm || !frames || playing}>
        {playing ? "再生中..." : "再生"}
      </button>
      <button onClick={handleExport} disabled={!vrm || !frames || playing}>
        {playing ? "再生・書き出し中..." : "動画として書き出す"}
      </button>
    </div>
  );
}

export default MdmPlayback;
