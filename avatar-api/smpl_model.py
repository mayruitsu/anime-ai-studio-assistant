"""SMPLモデル（.pklファイル）を読み込み、体型パラメータからメッシュ頂点を計算する。

SMPL公式配布の.pklは2010年代前半のPython/numpy APIを前提にしており、
依存ライブラリchumpyが現在のnumpy・Pythonでは読み込み時にエラーになる
(docs/tech/smpl-loading-compat.md参照)。ここではchumpy自体のコードは
書き換えず、読み込み前に実行時のみ後方互換エイリアスを追加することで対応する。
"""
import builtins
import inspect

import numpy as np

# chumpyが `from numpy import bool, int, float, ...` を実行するため、
# numpy 1.24+で削除されたこれらのエイリアスを実行時に一時的に復元する
for _name in ("bool", "int", "float", "complex", "object", "str"):
    if not hasattr(np, _name):
        setattr(np, _name, getattr(builtins, _name))
if not hasattr(np, "unicode"):
    np.unicode = str

# chumpyがPython 3.11で削除されたinspect.getargspecを使うための互換エイリアス
if not hasattr(inspect, "getargspec"):
    inspect.getargspec = inspect.getfullargspec

import pickle  # noqa: E402（上記の互換パッチをchumpy読み込みより前に適用する必要があるため）

import torch  # noqa: E402


class SmplModel:
    """SMPLの.pklから読み込んだテンプレート・ブレンドシェイプ・骨格情報を保持する。"""

    def __init__(self, pkl_path: str):
        with open(pkl_path, "rb") as f:
            data = pickle.load(f, encoding="latin1")

        self.v_template = torch.tensor(np.array(data["v_template"]), dtype=torch.float32)  # (6890, 3)
        self.shapedirs = torch.tensor(np.array(data["shapedirs"].r), dtype=torch.float32)  # (6890, 3, 300)
        self.posedirs = torch.tensor(np.array(data["posedirs"]), dtype=torch.float32)  # (6890, 3, 207)
        self.weights = torch.tensor(np.array(data["weights"]), dtype=torch.float32)  # (6890, 24)
        self.faces = torch.tensor(np.array(data["f"]).astype(np.int64))  # (13776, 3)
        self.kintree_table = np.array(data["kintree_table"])  # (2, 24)
        self.joint_regressor = torch.tensor(np.array(data["J_regressor"].todense()), dtype=torch.float32)  # (24, 6890)

    def shaped_template(self, betas: torch.Tensor) -> torch.Tensor:
        """体型パラメータ(β)を適用した、Tポーズのメッシュ頂点を返す。"""
        num_betas = betas.shape[0]
        shape_offset = torch.einsum("vcd,d->vc", self.shapedirs[:, :, :num_betas], betas)
        return self.v_template + shape_offset

    def joint_locations(self, vertices: torch.Tensor) -> torch.Tensor:
        """メッシュ頂点から関節位置を回帰する。"""
        return self.joint_regressor @ vertices


def write_obj(path: str, vertices: torch.Tensor, faces: torch.Tensor) -> None:
    """メッシュを簡易OBJ形式で書き出す（3Dビューアでの目視確認用）。"""
    with open(path, "w", encoding="utf-8") as f:
        for v in vertices.tolist():
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        for face in faces.tolist():
            f.write(f"f {face[0] + 1} {face[1] + 1} {face[2] + 1}\n")
