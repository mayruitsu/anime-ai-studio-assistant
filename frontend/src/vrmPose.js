// 指ボーン（親指のみMetacarpal始まり、他はProximal始まり）はループで機械的に生成する
const FINGER_JOINTS = {
  Thumb: ["Metacarpal", "Proximal", "Distal"],
  Index: ["Proximal", "Intermediate", "Distal"],
  Middle: ["Proximal", "Intermediate", "Distal"],
  Ring: ["Proximal", "Intermediate", "Distal"],
  Little: ["Proximal", "Intermediate", "Distal"],
};
const FINGER_BONE_NAMES = ["left", "right"].flatMap((side) =>
  Object.entries(FINGER_JOINTS).flatMap(([finger, joints]) =>
    joints.map((joint) => `${side}${finger}${joint}`)
  )
);

export const BONE_NAMES = [
  "head", "neck", "chest", "upperChest", "spine", "hips", "jaw", "leftEye", "rightEye",
  "leftShoulder", "rightShoulder",
  "leftUpperArm", "leftLowerArm", "leftHand",
  "rightUpperArm", "rightLowerArm", "rightHand",
  "leftUpperLeg", "leftLowerLeg", "leftFoot", "leftToes",
  "rightUpperLeg", "rightLowerLeg", "rightFoot", "rightToes",
  ...FINGER_BONE_NAMES,
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
