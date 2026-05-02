import { useState } from "react";
import ImageUploader from "./components/ImageUploader";
import PoseCanvas from "./components/PoseCanvas";
import FramePanel from "./components/FramePanel";

const INITIAL_POINTS = [
  { name: "nose",           x: 0.50, y: 0.08 },
  { name: "left_shoulder",  x: 0.35, y: 0.25 },
  { name: "right_shoulder", x: 0.65, y: 0.25 },
  { name: "left_elbow",     x: 0.25, y: 0.40 },
  { name: "right_elbow",    x: 0.75, y: 0.40 },
  { name: "left_wrist",     x: 0.20, y: 0.55 },
  { name: "right_wrist",    x: 0.80, y: 0.55 },
  { name: "left_hip",       x: 0.38, y: 0.55 },
  { name: "right_hip",      x: 0.62, y: 0.55 },
  { name: "left_knee",      x: 0.35, y: 0.73 },
  { name: "right_knee",     x: 0.65, y: 0.73 },
  { name: "left_ankle",     x: 0.33, y: 0.90 },
  { name: "right_ankle",    x: 0.67, y: 0.90 },
];

function App() {
  const [image, setImage] = useState(null);
  const [frames, setFrames] = useState([INITIAL_POINTS]);
  const [currentFrame, setCurrentFrame] = useState(0);

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
      <ImageUploader onUpload={setImage} />
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
