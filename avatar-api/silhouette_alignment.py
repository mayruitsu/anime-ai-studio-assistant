"""実写真から抽出したシルエットマスクを、正射影レンダラーのカメラ設定に合わせて
位置・スケールを揃えるための処理。

写真ごとに人物の写り具合（拡大率・位置）が異なるため、人物の縦方向の
バウンディングボックス（頭頂〜足元）が、基準となる比率に一致するよう
拡大縮小・平行移動する（正射影カメラのため回転・せん断は不要）。
"""
import cv2
import numpy as np


def mask_bbox_rows(mask: np.ndarray, threshold: float = 0.5):
    """マスクのうち前景(値>threshold)が存在する行の範囲(最小行, 最大行)を返す。"""
    rows = np.where((mask > threshold).any(axis=1))[0]
    return rows.min(), rows.max()


def align_mask_to_canvas(mask: np.ndarray, top_frac: float, bottom_frac: float, resolution: int) -> np.ndarray:
    """人物のバウンディングボックス上端・下端が基準比率(top_frac, bottom_frac)に
    一致するよう、マスクを拡大縮小・平行移動して(resolution, resolution)に変換する。
    横方向は前景の中心を画面中央に合わせる。
    """
    ys, xs = np.where(mask > 127)
    mask_top, mask_bottom = ys.min(), ys.max()
    # 横方向の中心は上半身（頭〜腰）だけで計算する。床の影が足元に写り込んでいると、
    # 全身で重心を取ると影の分だけ中心が偏ってしまうため
    upper_half = ys <= mask_top + (mask_bottom - mask_top) * 0.5
    mask_center_x = xs[upper_half].mean()

    scale = (bottom_frac - top_frac) * resolution / max(mask_bottom - mask_top, 1)
    tx = resolution / 2 - scale * mask_center_x
    ty = top_frac * resolution - scale * mask_top
    affine = np.array([[scale, 0, tx], [0, scale, ty]], dtype=np.float32)

    float_mask = (mask > 127).astype(np.float32)
    return cv2.warpAffine(float_mask, affine, (resolution, resolution), flags=cv2.INTER_LINEAR, borderValue=0)
