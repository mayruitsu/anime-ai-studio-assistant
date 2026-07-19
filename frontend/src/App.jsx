import { useState } from "react";
import ImageUploader from "./components/ImageUploader";
import PoseCanvas from "./components/PoseCanvas";
import FramePanel from "./components/FramePanel";

function App() {
  const [image, setImage] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [frames, setFrames] = useState([[]]);
  const [currentFrame, setCurrentFrame] = useState(0);

  const handleUpload = async (url, file) => {
    setImage(url);
    setImageFile(file);

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("http://localhost:8080/detect-pose", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();

    const points = data.landmarks.map(({ index, x, y }) => ({
      name: String(index),
      x,
      y,
    }));
    setFrames([points]);
    setCurrentFrame(0);
  };

  const handleExport = async () => {
    const formData = new FormData();
    formData.append("file", imageFile);
    formData.append("frames", JSON.stringify(frames));

    const res = await fetch("http://localhost:8080/export-video", {
      method: "POST",
      body: formData,
    });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "animation.mp4";
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePointsChange = (newPoints) => {
    setFrames((prev) =>
      prev.map((f, i) => (i === currentFrame ? newPoints : f))
    );
  };

  const handleAddFrame = () => {
    setFrames((prev) => [...prev, [...frames[currentFrame]]]);
    setCurrentFrame(frames.length);
  };

  return (
    <div style={{ padding: "24px" }}>
      <h1>アニメーションアシスタントAI</h1>
      <ImageUploader onUpload={handleUpload} />
      <FramePanel
        frames={frames}
        currentFrame={currentFrame}
        onSelect={setCurrentFrame}
        onAdd={handleAddFrame}
      />
      <PoseCanvas
        imageSrc={image}
        points={frames[currentFrame]}
        onPointsChange={handlePointsChange}
      />
      <button onClick={handleExport} disabled={!imageFile}>
        動画を書き出す
      </button>
    </div>
  );
}

export default App;
