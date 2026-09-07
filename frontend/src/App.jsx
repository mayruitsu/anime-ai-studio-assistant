import { useEffect, useRef, useState } from "react";
import VrmViewer from "./components/VrmViewer";
import BonePoser from "./components/BonePoser";
import KeyframeRecorder from "./components/KeyframeRecorder";
import MdmPlayback from "./components/MdmPlayback";
import { createToolRegistry, connectToolBridge } from "./toolBridge";
import { addKeyframe, exportKeyframeVideo } from "./keyframeActions";
import { generateMotionFromText, playAndExportMotion } from "./motionActions";

function App() {
  const [vrm, setVrm] = useState(null);
  const [modelUrl, setModelUrl] = useState(null);
  const [canvas, setCanvas] = useState(null);
  const [keyframes, setKeyframes] = useState([]);
  const [recording, setRecording] = useState(false);
  const stateRef = useRef({});
  stateRef.current = { vrm, canvas, keyframes };
  const motionJobsRef = useRef({});

  // 会話アシスタント向け：MDM生成は2〜3分かかるため、開始(job_id発行)と状態確認を分ける
  const handleStartMotionGeneration = (prompt) => {
    const jobId = crypto.randomUUID();
    motionJobsRef.current[jobId] = { status: "pending" };
    generateMotionFromText(prompt)
      .then((data) => { motionJobsRef.current[jobId] = { status: "done", frames: data.frames, text: data.text }; })
      .catch((err) => { motionJobsRef.current[jobId] = { status: "error", error: String(err) }; });
    return jobId;
  };
  const handleGetMotionGenerationStatus = (jobId) => motionJobsRef.current[jobId];
  const handlePlayAndExportGeneratedMotion = async (jobId) => {
    const job = motionJobsRef.current[jobId];
    if (job?.status !== "done") return false;
    await playAndExportMotion(stateRef.current.vrm, stateRef.current.canvas, job.frames);
    return true;
  };

  const handleAddKeyframe = () => setKeyframes((prev) => addKeyframe(stateRef.current.vrm, prev));
  const handleClearKeyframes = () => setKeyframes([]);
  const handleExportKeyframeVideo = async () => {
    setRecording(true);
    await exportKeyframeVideo(stateRef.current.vrm, stateRef.current.canvas, stateRef.current.keyframes);
    setRecording(false);
  };

  const handleLoadVrmFromUrl = (url) => {
    setVrm(null);
    setModelUrl(url);
  };

  useEffect(() => {
    const tools = createToolRegistry(() => stateRef.current.vrm, {
      addKeyframe: handleAddKeyframe,
      clearKeyframes: handleClearKeyframes,
      exportKeyframeVideo: handleExportKeyframeVideo,
      loadVrmModel: handleLoadVrmFromUrl,
      startMotionGeneration: handleStartMotionGeneration,
      getMotionGenerationStatus: handleGetMotionGenerationStatus,
      playAndExportGeneratedMotion: handlePlayAndExportGeneratedMotion,
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
