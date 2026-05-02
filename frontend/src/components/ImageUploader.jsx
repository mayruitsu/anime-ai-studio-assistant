import { useState } from "react";

function ImageUploader({ onUpload }) {
  const [preview, setPreview] = useState(null);

  const handleChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const url = URL.createObjectURL(file);
    setPreview(url);
    onUpload(url);
  };

  return (
    <div>
      <input type="file" accept="image/*" onChange={handleChange} />
      {preview && (
        <img src={preview} alt="アップロード画像" style={{ maxWidth: "500px", marginTop: "16px" }} />
      )}
    </div>
  );
}

export default ImageUploader;
