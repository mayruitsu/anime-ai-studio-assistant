import { useState } from "react";
import ImageUploader from "./components/ImageUploader";
import PoseCanvas from "./components/PoseCanvas";
import FramePanel from "./components/FramePanel";

function App() {
  const [image, setImage] = useState(null);
  const [frames, setFrames] = useState([[]]);
  const [currentFrame, setCurrentFrame] = useState(0);

  const handleUpload = async (url, file) => {
    setImage(url);

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
    </div>
  );
}

export default App;
