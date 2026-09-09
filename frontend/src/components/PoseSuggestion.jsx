import { useState } from "react";
import { applyPose } from "../vrmPose";
import { suggestNextPose } from "../poseSuggestionActions";

const HISTORY_SIZE = 2;

function PoseSuggestion({ vrm }) {
  const [text, setText] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSuggest = async () => {
    if (!vrm || !text) return;
    setLoading(true);
    try {
      // 呼び出し時点のVRMの姿勢（前回の提案＋手直し後）をそのまま「現在の姿勢」として使う
      const { currentPose, nextPose } = await suggestNextPose(vrm, history, text);
      applyPose(vrm, nextPose);
      setHistory((prev) => [...prev, currentPose].slice(-HISTORY_SIZE));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "16px" }}>
      <h3>AIに次の姿勢を提案してもらう（実験）</h3>
      <input
        type="text"
        placeholder="例：a person walks forward"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button onClick={handleSuggest} disabled={!vrm || !text || loading}>
        {loading ? "提案中..." : "次の姿勢を提案"}
      </button>
      <button onClick={() => setHistory([])} disabled={history.length === 0}>
        履歴をリセット（新しい動きを始める）
      </button>
      <p>
        提案された姿勢は関節ポーズ（上のスライダー）で手直しできます。気に入ったら
        キーフレームに追加してから、また提案してもらってください（履歴：{history.length}件）。
      </p>
    </div>
  );
}

export default PoseSuggestion;
