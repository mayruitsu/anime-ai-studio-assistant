import { useState } from "react";
import ImageUploader from "./components/ImageUploader";

function App() {
  const [image, setImage] = useState(null);

  return (
    <div style={{ padding: "24px" }}>
      <h1>アニメーションアシスタントAI</h1>
      <ImageUploader onUpload={setImage} />
      {image && <p>画像を読み込みました</p>}
    </div>
  );
}

export default App;
