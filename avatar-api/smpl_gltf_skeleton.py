"""SMPLの骨格・スキニング情報を、glTFのノード階層・スキン形式に変換する処理。

SMPLは頂点ごとの重み付き線形合成（Linear Blend Skinning）でメッシュを変形しており、
これはglTFのスキニング方式と数学的に同じ仕組みのため、変換は主にデータ形式
（SMPLの配列形式 -> glTFのノード階層・アクセサ形式）の変換になる。
"""
import numpy as np


def build_bind_pose_nodes(joints: np.ndarray, kintree_parents: list) -> list:
    """Tポーズ（bind pose）での各関節のノード情報（親からの相対位置）を返す。

    各要素は{"parent": 親関節のインデックス（ルートはNone）, "translation": (x,y,z)}。
    ルート以外は親関節からの相対オフセット、ルートは原点からの絶対位置
    （smpl_lbs.forward_kinematicsのlocal[k,:3,3]の計算と同じ関係）。
    """
    nodes = []
    for k in range(len(kintree_parents)):
        if k == 0:
            nodes.append({"parent": None, "translation": tuple(float(v) for v in joints[k])})
        else:
            parent = kintree_parents[k]
            offset = joints[k] - joints[parent]
            nodes.append({"parent": parent, "translation": tuple(float(v) for v in offset)})
    return nodes


def inverse_bind_matrices(joints: np.ndarray) -> np.ndarray:
    """各関節のinverse bind matrix (24, 4, 4) を返す。

    bind pose（Tポーズ）は全関節の回転が単位行列なので、各関節のグローバル変換は
    平行移動のみ。したがってinverse bind matrixは「関節位置だけ原点に戻す」平行移動になる。
    """
    n = joints.shape[0]
    mats = np.tile(np.eye(4, dtype=np.float32), (n, 1, 1))
    mats[:, :3, 3] = -joints
    return mats


def top4_skin_weights(weights: np.ndarray) -> tuple:
    """SMPLの頂点ごとの重み(V, 24)から、glTF形式（頂点ごと関節4つ・重み4つ）に変換する。

    glTFは頂点ごとに影響する関節を最大4つまでしか扱えないため、重みが大きい上位4つを選び、
    合計が1になるよう正規化する（SMPLの重みは非負でほぼ疎なため、5つ以上の非ゼロ重みを
    持つ頂点はごく少数と見込まれる）。
    """
    top4_idx = np.argsort(-weights, axis=1)[:, :4]
    top4_val = np.take_along_axis(weights, top4_idx, axis=1)
    row_sums = top4_val.sum(axis=1, keepdims=True)
    top4_val = top4_val / np.clip(row_sums, 1e-8, None)
    return top4_idx.astype(np.uint16), top4_val.astype(np.float32)
