import { useState } from "react";

function ImageUploader({ onUpload }) {
  const handleChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const url = URL.createObjectURL(file);
    onUpload(url, file);
  };

  return (
    <div>
      <input type="file" accept="image/*" onChange={handleChange} />
    </div>
  );
}

export default ImageUploader;
