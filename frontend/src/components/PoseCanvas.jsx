import { useEffect, useRef } from "react";

const MOCK_POINTS = [
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

function PoseCanvas({ imageSrc }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!imageSrc) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const img = new Image();

    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);

      MOCK_POINTS.forEach(({ x, y }) => {
        ctx.beginPath();
        ctx.arc(x * img.width, y * img.height, 6, 0, Math.PI * 2);
        ctx.fillStyle = "red";
        ctx.fill();
      });
    };

    img.src = imageSrc;
  }, [imageSrc]);

  return <canvas ref={canvasRef} style={{ maxWidth: "500px" }} />;
}

export default PoseCanvas;
