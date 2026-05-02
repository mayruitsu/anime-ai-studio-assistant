import { useEffect, useRef } from "react";

function PoseCanvas({ imageSrc, points, onPointsChange }) {
  const canvasRef = useRef(null);
  const imageRef = useRef(null);
  const dragging = useRef(null);

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
    onPointsChange(
      points.map((p, i) => (i === dragging.current ? { ...p, x, y } : p))
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
