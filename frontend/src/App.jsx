import { useState } from "react";
import ImageUploader from "./components/ImageUploader";
import PoseCanvas from "./components/PoseCanvas";

function App() {
  const [image, setImage] = useState(null);

  return (
    <div style={{ padding: "24px" }}>
      <h1>アニメーションアシスタントAI</h1>
      <ImageUploader onUpload={setImage} />
      <PoseCanvas imageSrc={image} />
    </div>
  );
}

export default App;
