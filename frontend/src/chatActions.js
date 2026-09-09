export async function sendChatMessage(messages) {
  const res = await fetch("http://localhost:8092/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  });
  return res.json();
}
