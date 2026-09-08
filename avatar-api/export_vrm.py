"""SMPLでフィッティングした体型(β)をVRM 1.0形式でエクスポートする。

学習済みAIモデルは使わず、SMPLの骨格・スキニング情報を純粋なデータ変換で
glTF/VRM形式に変換する（数学的な仕組みはsmpl_gltf_skeleton.py参照）。
現時点では体型（β）のみを反映し、テクスチャ・服・顔などの見た目は含まない
（プレースホルダーとして肌色の単色マテリアルを設定する）。
"""
import argparse

import numpy as np
import pygltflib
import torch

from gltf_buffer_builder import GltfBufferBuilder
from smpl_gltf_skeleton import build_bind_pose_nodes, inverse_bind_matrices, top4_skin_weights
from smpl_model import SmplModel
from vrm_export_helpers import SMPL_TO_VRM, build_vrm_extension, compute_vertex_normals


def export_vrm(model: SmplModel, betas: torch.Tensor, output_path: str):
    # betasがモデルと異なるdevice（例：GPUで最適化した結果をCPU用モデルに渡す等）でも
    # 動くよう、シェイプ済みメッシュ・関節位置の計算はmodel側のdeviceで統一してから
    # numpyに変換する
    v_shaped_t = model.shaped_template(betas.to(model.v_template.device))
    joints = model.joint_locations(v_shaped_t).detach().cpu().numpy().astype(np.float32)
    v_shaped = v_shaped_t.detach().cpu().numpy().astype(np.float32)
    faces = model.faces.cpu().numpy().astype(np.uint32)
    weights = model.weights.cpu().numpy()
    kintree_parents = model.kintree_table[0].astype(int).tolist()
    kintree_parents[0] = 0
    num_joints = len(kintree_parents)

    joint_nodes = build_bind_pose_nodes(joints, kintree_parents)
    # SMPLの原点は骨盤付近だがVRMは「足が地面(y=0)」を前提とするため、ルートの
    # 平行移動にオフセットを加える（スキニングの仕組み上、これでメッシュ全体が動く）
    floor_offset_y = float(-v_shaped[:, 1].min())
    root_x, root_y, root_z = joint_nodes[0]["translation"]
    joint_nodes[0]["translation"] = (root_x, root_y + floor_offset_y, root_z)
    inv_bind = inverse_bind_matrices(joints)
    inv_bind_flat = inv_bind.transpose(0, 2, 1).reshape(num_joints, 16).astype(np.float32)  # glTFは列優先
    skin_joint_idx, skin_weight_val = top4_skin_weights(weights)
    normals = compute_vertex_normals(v_shaped, faces)

    gltf = pygltflib.GLTF2()
    builder = GltfBufferBuilder(gltf)
    pos_idx = builder.add(v_shaped, pygltflib.FLOAT, "VEC3", target=pygltflib.ARRAY_BUFFER, with_minmax=True)
    norm_idx = builder.add(normals, pygltflib.FLOAT, "VEC3", target=pygltflib.ARRAY_BUFFER)
    indices_idx = builder.add(faces.reshape(-1), pygltflib.UNSIGNED_INT, "SCALAR", target=pygltflib.ELEMENT_ARRAY_BUFFER)
    joints_idx = builder.add(skin_joint_idx, pygltflib.UNSIGNED_SHORT, "VEC4", target=pygltflib.ARRAY_BUFFER)
    weights_idx = builder.add(skin_weight_val, pygltflib.FLOAT, "VEC4", target=pygltflib.ARRAY_BUFFER)
    inv_bind_idx = builder.add(inv_bind_flat, pygltflib.FLOAT, "MAT4")

    children_of = {k: [] for k in range(num_joints)}
    for k, info in enumerate(joint_nodes):
        if info["parent"] is not None:
            children_of[info["parent"]].append(k)
    for k, info in enumerate(joint_nodes):
        name = SMPL_TO_VRM.get(k, f"smpl_joint_{k}")
        gltf.nodes.append(pygltflib.Node(name=name, translation=list(info["translation"]),
                                          children=children_of[k] or None))
    root_joint_node = 0

    material_idx = 0
    gltf.materials.append(pygltflib.Material(
        pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(baseColorFactor=[0.87, 0.72, 0.60, 1.0]),
    ))
    gltf.meshes.append(pygltflib.Mesh(primitives=[pygltflib.Primitive(
        attributes=pygltflib.Attributes(POSITION=pos_idx, NORMAL=norm_idx, JOINTS_0=joints_idx, WEIGHTS_0=weights_idx),
        indices=indices_idx, material=material_idx,
    )]))
    gltf.skins.append(pygltflib.Skin(
        inverseBindMatrices=inv_bind_idx, joints=list(range(num_joints)), skeleton=root_joint_node,
    ))
    mesh_node = len(gltf.nodes)
    gltf.nodes.append(pygltflib.Node(mesh=0, skin=0, name="body"))

    gltf.scenes.append(pygltflib.Scene(nodes=[root_joint_node, mesh_node]))
    gltf.scene = 0

    bone_to_node = {name: idx for idx, name in enumerate(
        [SMPL_TO_VRM.get(k) for k in range(num_joints)]) if name is not None}
    gltf.extensionsUsed = ["VRMC_vrm"]
    gltf.extensions = {"VRMC_vrm": build_vrm_extension(bone_to_node)}

    blob = builder.finalize()
    gltf.set_binary_blob(blob)
    gltf.save_binary(output_path)


def main():
    parser = argparse.ArgumentParser(description="SMPLの体型パラメータをVRM 1.0形式でエクスポートする")
    parser.add_argument("pkl_path")
    parser.add_argument("output_path", help="出力する.vrmファイルのパス")
    parser.add_argument("--betas", type=float, nargs="+", default=None, help="体型パラメータ(β、10次元、省略時は全て0)")
    args = parser.parse_args()

    model = SmplModel(args.pkl_path)
    betas = torch.tensor(args.betas, dtype=torch.float32) if args.betas else torch.zeros(10)
    export_vrm(model, betas, args.output_path)
    print(f"VRMファイルを{args.output_path}に書き出しました")


if __name__ == "__main__":
    main()
