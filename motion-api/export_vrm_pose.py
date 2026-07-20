import json
import sys
import numpy as np
import torch

from utils.rotation_conversions import rotation_6d_to_matrix, matrix_to_euler_angles

# SMPL 24関節 -> VRM humanoidボーン名 の対応表
SMPL_TO_VRM = {
    0: "hips",
    1: "leftUpperLeg",
    2: "rightUpperLeg",
    3: "spine",
    4: "leftLowerLeg",
    5: "rightLowerLeg",
    6: "chest",
    7: "leftFoot",
    8: "rightFoot",
    12: "neck",
    15: "head",
    16: "leftUpperArm",
    17: "rightUpperArm",
    18: "leftLowerArm",
    19: "rightLowerArm",
    20: "leftHand",
    21: "rightHand",
}


def smpl_params_to_vrm_pose(smpl_params_path: str) -> dict:
    data = np.load(smpl_params_path, allow_pickle=True).item()
    thetas = torch.from_numpy(data["thetas"])  # (24, 6, frames)
    num_frames = thetas.shape[-1]

    frames = []
    for f in range(num_frames):
        pose = {}
        for smpl_idx, bone_name in SMPL_TO_VRM.items():
            d6 = thetas[smpl_idx, :, f].unsqueeze(0)
            mat = rotation_6d_to_matrix(d6)
            euler = matrix_to_euler_angles(mat, "XYZ")[0]
            pose[bone_name] = {"x": float(euler[0]), "y": float(euler[1]), "z": float(euler[2])}
        frames.append(pose)

    return {"text": str(data["text"]), "frames": frames}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("使い方: python export_vrm_pose.py <smpl_params.npyのパス> <出力先.json>")
    else:
        result = smpl_params_to_vrm_pose(sys.argv[1])
        with open(sys.argv[2], "w") as f:
            json.dump(result, f)
        print(f"{len(result['frames'])}フレームを{sys.argv[2]}に書き出しました")
