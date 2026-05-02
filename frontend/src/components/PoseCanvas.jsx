import { useEffect, useRef, useState } from "react";

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

function PoseCanvas({ imageSrc }) {
  const canvasRef = useRef(null);
  const imageRef = useRef(null);
  const dragging = useRef(null);
  const [points, setPoints] = useState(INITIAL_POINTS);

  const draw = (pts) => {
    const canvas = canvasRef.current;
    const img = imageRef.current;
    if (!canvas || !img) return;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0);
    pts.forEach(({ x, y }) => {
      ctx.beginPath();
      ctx.arc(x * img.width, y * img.height, 6, 0, Math.PI * 2);
      ctx.fillStyle = "red";
      ctx.fill();
    });
  };

  useEffect(() => {
    if (!imageSrc) return;
    const img = new Image();
    img.onload = () => {
      const canvas = canvasRef.current;
      canvas.width = img.width;
      canvas.height = img.height;
      imageRef.current = img;
      draw(points);
    };
    img.src = imageSrc;
  }, [imageSrc]);

  useEffect(() => {
    draw(points);
  }, [points]);

  const getPos = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    return {
      x: (e.clientX - rect.left) / rect.width,
      y: (e.clientY - rect.top) / rect.height,
    };
  };

  const handleMouseDown = (e) => {
    const { x, y } = getPos(e);
    const idx = points.findIndex((p) => Math.hypot(p.x - x, p.y - y) < 0.03);
    if (idx !== -1) dragging.current = idx;
  };

  const handleMouseMove = (e) => {
    if (dragging.current === null) return;
    const { x, y } = getPos(e);
    setPoints((prev) =>
      prev.map((p, i) => (i === dragging.current ? { ...p, x, y } : p))
    );
  };

  const handleMouseUp = () => {
    dragging.current = null;
  };

  return (
    <canvas
      ref={canvasRef}
      style={{ maxWidth: "500px" }}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
    />
  );
}

export default PoseCanvas;
