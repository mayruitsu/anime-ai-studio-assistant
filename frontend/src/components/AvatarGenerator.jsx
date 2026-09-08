import { useState } from "react";
import { generateAvatarFromPhotos } from "../avatarActions";

function AvatarGenerator({ onVrmGenerated }) {
  const [files, setFiles] = useState({ front: null, back: null, side: null });
  const [sideIsRight, setSideIsRight] = useState(false);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);

  const handleFile = (key) => (e) => setFiles((prev) => ({ ...prev, [key]: e.target.files[0] }));

  const handleGenerate = async () => {
    if (!files.front || !files.back || !files.side) return;
    setStatus("generating");
    setError(null);
    try {
      const url = await generateAvatarFromPhotos({ ...files, sideIsRight });
      onVrmGenerated(url);
      setStatus("done");
    } catch (err) {
      setError(String(err));
      setStatus("error");
    }
  };

  return (
    <div style={{ padding: "16px", border: "1px solid #ccc", marginTop: "8px" }}>
      <h3>写真からアバターを生成（実験）</h3>
      <div>正面：<input type="file" accept="image/*" onChange={handleFile("front")} /></div>
      <div>背面：<input type="file" accept="image/*" onChange={handleFile("back")} /></div>
      <div>側面：<input type="file" accept="image/*" onChange={handleFile("side")} /></div>
      <label>
        <input type="checkbox" checked={sideIsRight} onChange={(e) => setSideIsRight(e.target.checked)} />
        側面写真は右側面
      </label>
      <div>
        <button onClick={handleGenerate} disabled={status === "generating"}>
          {status === "generating" ? "生成中…（数十秒かかります）" : "アバターを生成"}
        </button>
      </div>
      {status === "error" && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default AvatarGenerator;
