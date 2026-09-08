"""VRMエクスポート用の小さなヘルパー（頂点法線の計算、VRM 1.0拡張JSONの組み立て）。

SMPLの24関節のうち主要な18個をVRM humanoidボーン名に対応付ける表は、
anime-ai-studio-assistant/motion-api/export_vrm_pose.py（モーション再生用）で
既に使われているものと同じ対応関係を採用している。
"""
import numpy as np

SMPL_TO_VRM = {
    0: "hips", 1: "leftUpperLeg", 2: "rightUpperLeg", 3: "spine",
    4: "leftLowerLeg", 5: "rightLowerLeg", 6: "chest", 7: "leftFoot", 8: "rightFoot",
    12: "neck", 13: "leftShoulder", 14: "rightShoulder", 15: "head",
    16: "leftUpperArm", 17: "rightUpperArm", 18: "leftLowerArm", 19: "rightLowerArm",
    20: "leftHand", 21: "rightHand",
}


def compute_vertex_normals(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    """三角形メッシュの頂点法線を計算する（各面の法線を、それを共有する頂点に加算して正規化）。"""
    normals = np.zeros_like(vertices)
    v0, v1, v2 = vertices[faces[:, 0]], vertices[faces[:, 1]], vertices[faces[:, 2]]
    face_normals = np.cross(v1 - v0, v2 - v0)
    for i in range(3):
        np.add.at(normals, faces[:, i], face_normals)
    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    return (normals / np.clip(lengths, 1e-8, None)).astype(np.float32)


def build_vrm_extension(bone_to_node: dict) -> dict:
    """VRM 1.0拡張（VRMC_vrm）のJSONを組み立てる。必須フィールド（meta.name,
    meta.authors, meta.licenseUrl, humanoid.humanBones）のみを設定する。
    """
    return {
        "specVersion": "1.0",
        "meta": {
            "name": "self-model-experiment fitted avatar",
            "authors": ["self-model-experiment"],
            "licenseUrl": "https://vrm.dev/licenses/1.0/",
        },
        "humanoid": {
            "humanBones": {name: {"node": idx} for name, idx in bone_to_node.items()},
        },
    }
