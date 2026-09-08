"""glTFのバイナリバッファ・バッファビュー・アクセサを組み立てるための汎用ヘルパー。

SMPL固有の知識は持たず、numpy配列をglTFの1つのバイナリblobに追記しながら
対応するbufferView・accessorを登録していく、形式変換のみを担当する。
"""
import numpy as np
import pygltflib


class GltfBufferBuilder:
    """1本のバイナリバッファに、配列を追記しながらbufferView・accessorを作る。"""

    def __init__(self, gltf: pygltflib.GLTF2):
        self.gltf = gltf
        self.blob_parts = []
        self.cursor = 0

    def add(self, array: np.ndarray, component_type: int, accessor_type: str,
            target: int = None, with_minmax: bool = False) -> int:
        """配列を追記し、作成したaccessorのインデックスを返す。"""
        data = array.tobytes()
        # 各bufferViewの開始位置を4バイト境界に揃える（glTFの慣例的な要件）
        pad = (-len(data)) % 4
        if pad:
            data = data + b"\x00" * pad

        buffer_view = pygltflib.BufferView(
            buffer=0, byteOffset=self.cursor, byteLength=len(array.tobytes()), target=target,
        )
        self.gltf.bufferViews.append(buffer_view)
        bv_index = len(self.gltf.bufferViews) - 1

        accessor = pygltflib.Accessor(
            bufferView=bv_index, componentType=component_type, count=array.shape[0], type=accessor_type,
        )
        if with_minmax:
            flat = array.reshape(array.shape[0], -1)
            accessor.min = flat.min(axis=0).tolist()
            accessor.max = flat.max(axis=0).tolist()
        self.gltf.accessors.append(accessor)

        self.blob_parts.append(data)
        self.cursor += len(data)
        return len(self.gltf.accessors) - 1

    def finalize(self) -> bytes:
        """これまでに追記したデータを1本のバイナリblobにまとめ、Bufferを登録する。"""
        blob = b"".join(self.blob_parts)
        self.gltf.buffers.append(pygltflib.Buffer(byteLength=len(blob)))
        return blob
