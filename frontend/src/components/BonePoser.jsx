import { useState } from "react";

const BONE_NAMES = [
  "head", "neck", "chest", "spine", "hips",
  "leftUpperArm", "leftLowerArm", "leftHand",
  "rightUpperArm", "rightLowerArm", "rightHand",
  "leftUpperLeg", "leftLowerLeg", "leftFoot",
  "rightUpperLeg", "rightLowerLeg", "rightFoot",
];

function BonePoser({ vrm }) {
  const [boneName, setBoneName] = useState(BONE_NAMES[0]);
  const [rotation, setRotation] = useState({ x: 0, y: 0, z: 0 });

  const boneNode = vrm?.humanoid?.getNormalizedBoneNode(boneName);

  const handleSelectBone = (e) => {
    const name = e.target.value;
    setBoneName(name);
    const node = vrm?.humanoid?.getNormalizedBoneNode(name);
    setRotation({
      x: node?.rotation.x ?? 0,
      y: node?.rotation.y ?? 0,
      z: node?.rotation.z ?? 0,
    });
  };

  const handleChangeAxis = (axis) => (e) => {
    const value = Number(e.target.value);
    const next = { ...rotation, [axis]: value };
    setRotation(next);
    if (boneNode) boneNode.rotation[axis] = value;
  };

  return (
    <div style={{ padding: "16px" }}>
      <label>
        関節：
        <select value={boneName} onChange={handleSelectBone}>
          {BONE_NAMES.map((name) => (
            <option key={name} value={name}>{name}</option>
          ))}
        </select>
      </label>
      {["x", "y", "z"].map((axis) => (
        <div key={axis}>
          <label>
            {axis.toUpperCase()}軸回転：
            <input
              type="range"
              min={-Math.PI}
              max={Math.PI}
              step={0.01}
              value={rotation[axis]}
              onChange={handleChangeAxis(axis)}
            />
          </label>
        </div>
      ))}
    </div>
  );
}

export default BonePoser;
