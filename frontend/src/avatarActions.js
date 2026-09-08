export async function generateAvatarFromPhotos({ front, back, side, sideIsRight }) {
  const formData = new FormData();
  formData.append("front", front);
  formData.append("back", back);
  formData.append("side", side);
  formData.append("side_is_right", String(!!sideIsRight));

  const res = await fetch("http://localhost:8091/fit-avatar", { method: "POST", body: formData });
  if (!res.ok) throw new Error(`avatar-apiの呼び出しに失敗しました (HTTP ${res.status})`);
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}
