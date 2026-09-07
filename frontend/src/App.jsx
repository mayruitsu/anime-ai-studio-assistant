import { useEffect, useRef, useState } from "react";
import VrmViewer from "./components/VrmViewer";
import BonePoser from "./components/BonePoser";
import KeyframeRecorder from "./components/KeyframeRecorder";
import MdmPlayback from "./components/MdmPlayback";
import { createToolRegistry, connectToolBridge } from "./toolBridge";
import { addKeyframe, exportKeyframeVideo } from "./keyframeActions";

function App() {
  const [vrm, setVrm] = useState(null);
  const [modelUrl, setModelUrl] = useState(null);
  const [canvas, setCanvas] = useState(null);
  const [keyframes, setKeyframes] = useState([]);
  const [recording, setRecording] = useState(false);
  const stateRef = useRef({});
  stateRef.current = { vrm, canvas, keyframes };

  const handleAddKeyframe = () => setKeyframes((prev) => addKeyframe(stateRef.current.vrm, prev));
  const handleClearKeyframes = () => setKeyframes([]);
  const handleExportKeyframeVideo = async () => {
    setRecording(true);
    await exportKeyframeVideo(stateRef.current.vrm, stateRef.current.canvas, stateRef.current.keyframes);
    setRecording(false);
  };

  useEffect(() => {
    const tools = createToolRegistry(() => stateRef.current.vrm, {
      addKeyframe: handleAddKeyframe,
      clearKeyframes: handleClearKeyframes,
      exportKeyframeVideo: handleExportKeyframeVideo,
    });
    const ws = connectToolBridge("ws://localhost:8080/ws/tools", tools);
    return () => ws.close();
  }, []);

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
        {modelUrl && (
          <VrmViewer modelUrl={modelUrl} onVrmLoaded={setVrm} onCanvasReady={setCanvas} />
        )}
        <div>
          <BonePoser vrm={vrm} />
          <KeyframeRecorder
            vrm={vrm}
            keyframes={keyframes}
            recording={recording}
            onAddKeyframe={handleAddKeyframe}
            onClear={handleClearKeyframes}
            onExport={handleExportKeyframeVideo}
          />
          <MdmPlayback vrm={vrm} canvas={canvas} />
        </div>
      </div>
    </div>
  );
}

export default App;
