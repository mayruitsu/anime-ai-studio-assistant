import { useState } from "react";
import VrmViewer from "./components/VrmViewer";
import BonePoser from "./components/BonePoser";

function App() {
  const [vrm, setVrm] = useState(null);
  const [modelUrl, setModelUrl] = useState(null);

  const handleSelectFile = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setVrm(null);
    setModelUrl(URL.createObjectURL(file));
  };

  return (
    <div style={{ padding: "24px" }}>
      <h1>アニメーションアシスタントAI（3Dモデルポージング）</h1>
      <input type="file" accept=".vrm" onChange={handleSelectFile} />
      <div style={{ display: "flex" }}>
        {modelUrl && <VrmViewer modelUrl={modelUrl} onVrmLoaded={setVrm} />}
        <BonePoser vrm={vrm} />
      </div>
    </div>
  );
}

export default App;
