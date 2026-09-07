export const BONE_NAMES = [
  "head", "neck", "chest", "spine", "hips",
  "leftUpperArm", "leftLowerArm", "leftHand",
  "rightUpperArm", "rightLowerArm", "rightHand",
  "leftUpperLeg", "leftLowerLeg", "leftFoot",
  "rightUpperLeg", "rightLowerLeg", "rightFoot",
];

export function capturePose(vrm) {
  const pose = {};
  for (const name of BONE_NAMES) {
    const node = vrm.humanoid?.getNormalizedBoneNode(name);
    if (node) pose[name] = { x: node.rotation.x, y: node.rotation.y, z: node.rotation.z };
  }
  return pose;
}

export function applyPose(vrm, pose) {
  for (const name of Object.keys(pose)) {
    const node = vrm.humanoid?.getNormalizedBoneNode(name);
    if (node) node.rotation.set(pose[name].x, pose[name].y, pose[name].z);
  }
}

export function lerpPose(a, b, t) {
  const result = {};
  for (const name of Object.keys(a)) {
    result[name] = {
      x: a[name].x + (b[name].x - a[name].x) * t,
      y: a[name].y + (b[name].y - a[name].y) * t,
      z: a[name].z + (b[name].z - a[name].z) * t,
    };
  }
  return result;
}
