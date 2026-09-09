import { useState } from "react";
import { sendChatMessage } from "../chatActions";

function ChatBox() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  const handleSend = async () => {
    if (!input) return;
    const nextMessages = [...messages, { role: "user", content: input }];
    setMessages(nextMessages);
    setInput("");
    setSending(true);
    try {
      // ツール呼び出しは/tools/call経由でWebSocketブリッジを通してブラウザ側に実行される
      // （App.jsxのconnectToolBridge、既存の仕組みをそのまま利用）
      const data = await sendChatMessage(nextMessages);
      setMessages((prev) => [...prev, { role: "assistant", content: data.reply, toolCall: data.tool_call }]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div style={{ padding: "16px" }}>
      <h3>会話でポーズを調整（実験）</h3>
      <div style={{ maxHeight: "200px", overflowY: "auto", border: "1px solid #ccc", padding: "8px" }}>
        {messages.map((m, i) => (
          <div key={i}>
            <b>{m.role === "user" ? "あなた" : "AI"}：</b>{m.content}
            {m.toolCall && <div style={{ color: "#888" }}>（実行：{m.toolCall.tool}）</div>}
          </div>
        ))}
      </div>
      <input
        type="text"
        placeholder="例：左手を上げて"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSend()}
      />
      <button onClick={handleSend} disabled={!input || sending}>
        {sending ? "送信中..." : "送信"}
      </button>
    </div>
  );
}

export default ChatBox;
