"""単色背景を前提とした、学習済みAIモデルに頼らないシルエット抽出（背景除去）。

画像四隅の色を背景色として推定し、各ピクセルの色が背景色からどれだけ
離れているかだけでシルエット（前景マスク）を作る、古典的な色閾値方式。
"""
import argparse

import cv2
import numpy as np


def estimate_background_color(image: np.ndarray, margin: int = 10) -> np.ndarray:
    """画像四隅のパッチから背景色を推定する（単色背景が前提）。"""
    h, w = image.shape[:2]
    corners = [
        image[:margin, :margin],
        image[:margin, w - margin:],
        image[h - margin:, :margin],
        image[h - margin:, w - margin:],
    ]
    samples = np.concatenate([c.reshape(-1, 3) for c in corners], axis=0)
    return samples.mean(axis=0)


def extract_silhouette(image: np.ndarray, threshold: float = 40.0) -> np.ndarray:
    """背景色からのユークリッド距離が閾値を超えるピクセルを前景(255)とする2値マスクを返す。

    単色・無地の背景が画像全体（四隅含む）を覆っている場合のみ有効。
    背景に物が写り込む場合は`extract_silhouette_grabcut`を使う。
    """
    bg_color = estimate_background_color(image)
    diff = image.astype(np.float32) - bg_color
    distance = np.linalg.norm(diff, axis=2)
    mask = np.where(distance > threshold, 255, 0).astype(np.uint8)
    # 単一光源の写り込みで生じる小さな穴・ノイズを除去する
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return mask


def extract_silhouette_grabcut(image: np.ndarray, margin_ratio: float = 0.03, iterations: int = 5) -> np.ndarray:
    """GrabCut（学習済みAIを使わない古典的な色分布ベースの領域分割）でシルエットを抽出する。

    四隅の色だけを見る`extract_silhouette`と違い、背景に物が写り込んで四隅の
    色推定が不正確になる場合でも、画像全体の色分布から前景・背景を推定できる。
    画像の外周`margin_ratio`分を「確実な背景」、それより内側を「前景候補」として
    GrabCutの反復最適化にかける。
    """
    h, w = image.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    mx, my = int(w * margin_ratio), int(h * margin_ratio)
    rect = (mx, my, w - 2 * mx, h - 2 * my)

    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    cv2.grabCut(image, mask, rect, bgd_model, fgd_model, iterations, cv2.GC_INIT_WITH_RECT)

    foreground = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    kernel = np.ones((5, 5), np.uint8)
    foreground = cv2.morphologyEx(foreground, cv2.MORPH_OPEN, kernel)
    foreground = cv2.morphologyEx(foreground, cv2.MORPH_CLOSE, kernel)
    return foreground


def estimate_background_gradient(image: np.ndarray, border: int = 30) -> np.ndarray:
    """画像の外周ピクセルから、背景の明暗のグラデーション（照明のムラ）を
    チャンネルごとに2次曲面 bg(x, y) = a + b*x + c*y + d*x^2 + e*y^2 + f*x*y
    として推定し、画像全体に外挿した背景色マップを返す。中心から周辺にかけて
    暗くなるビネットのような、円形に近い明暗ムラは1次の平面では近似できないため、
    2次項を含めている。
    """
    h, w = image.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    edge_mask = np.zeros((h, w), dtype=bool)
    edge_mask[:border, :] = True
    edge_mask[-border:, :] = True
    edge_mask[:, :border] = True
    edge_mask[:, -border:] = True

    ex, ey = xx[edge_mask].astype(np.float64), yy[edge_mask].astype(np.float64)
    design = np.stack([ex, ey, ex ** 2, ey ** 2, ex * ey, np.ones_like(ex)], axis=1)
    full_terms = [xx, yy, xx ** 2, yy ** 2, xx * yy, np.ones_like(xx)]

    bg_map = np.zeros_like(image, dtype=np.float32)
    for c in range(image.shape[2]):
        values = image[..., c][edge_mask].astype(np.float64)
        coeffs, *_ = np.linalg.lstsq(design, values, rcond=None)
        bg_map[..., c] = sum(coef * term for coef, term in zip(coeffs, full_terms))
    return bg_map


def remove_cast_shadow(image: np.ndarray, bg_map: np.ndarray, mask: np.ndarray,
                        value_ratio_range: tuple = (0.25, 0.95),
                        hue_tolerance: float = 25.0, sat_tolerance: float = 60.0) -> np.ndarray:
    """床の影を前景マスクから取り除く（学習を使わない古典的な影検出）。

    影は「明るさ(Value)だけが背景より暗く、色相(Hue)・彩度(Saturation)は
    背景とほぼ変わらない」という性質を持つ（Cucchiara et al.のHSVベースの
    影検出と同じ考え方）。この性質に当てはまるピクセルを影とみなし、前景から除外する。
    """
    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv_bg = cv2.cvtColor(np.clip(bg_map, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)

    v_ratio = hsv_img[..., 2] / np.clip(hsv_bg[..., 2], 1e-3, None)
    sat_diff = np.abs(hsv_img[..., 1] - hsv_bg[..., 1])
    hue_diff = np.abs(hsv_img[..., 0] - hsv_bg[..., 0])
    hue_diff = np.minimum(hue_diff, 180 - hue_diff)  # OpenCVのHueは0〜180の循環値

    is_shadow = (
        (v_ratio > value_ratio_range[0]) & (v_ratio < value_ratio_range[1])
        & (sat_diff < sat_tolerance) & (hue_diff < hue_tolerance)
    )
    cleaned = mask.copy()
    cleaned[is_shadow] = 0
    return cleaned


def fill_enclosed_holes(mask: np.ndarray) -> np.ndarray:
    """前景に完全に囲まれた穴だけを埋める（外の背景とつながっている領域は埋めない）。

    無彩色の服など、`remove_cast_shadow`が服の内部で誤って影と判定してしまう
    小さな穴を埋めたいが、床の影のように外の背景と地続きの領域まで
    再びつなげてしまわないようにするため、単純なクロージングではなく
    floodFillで「外から到達できない背景領域＝穴」だけを特定する。
    """
    h, w = mask.shape
    flood = mask.copy()
    flood_fill_mask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(flood, flood_fill_mask, (0, 0), 255)
    unreachable_background = cv2.bitwise_not(flood)
    return mask | unreachable_background


def extract_silhouette_gradient(image: np.ndarray, threshold: float = 40.0, border: int = 30,
                                 remove_shadow: bool = False) -> np.ndarray:
    """背景の照明グラデーションを考慮したシルエット抽出。

    `extract_silhouette`は背景色を画像全体で1つの定数として扱うため、周辺が
    暗くなるビネット等の明暗ムラがあると誤判定しやすい。こちらは画像の外周
    ピクセルから背景の明暗の傾きを推定し、位置ごとの背景推定値との距離で判定する。

    `remove_shadow=True`にすると床の影を`remove_cast_shadow`で除去できるが、
    無彩色（グレー等）の服では色相のノイズにより服の内部に穴が開く副作用がある。
    体の輪郭が欠けることの方が後段のSMPLフィッティングへの悪影響が大きいと
    考えられるため、デフォルトは無効にしている（影は体から離れた孤立領域なので、
    微分可能レンダリングの輪郭付近の勾配にはほぼ影響しない見込み）。
    """
    bg_map = estimate_background_gradient(image, border)
    diff = image.astype(np.float32) - bg_map
    distance = np.linalg.norm(diff, axis=2)
    mask = np.where(distance > threshold, 255, 0).astype(np.uint8)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    if remove_shadow:
        mask = remove_cast_shadow(image, bg_map, mask)
        mask = fill_enclosed_holes(mask)
    return mask


def main():
    parser = argparse.ArgumentParser(description="単色背景写真からシルエットマスクを抽出する")
    parser.add_argument("input", help="入力画像のパス")
    parser.add_argument("output", help="出力するマスク画像のパス")
    parser.add_argument("--threshold", type=float, default=40.0, help="背景色からの距離の閾値")
    parser.add_argument("--method", choices=["threshold", "grabcut", "gradient"], default="threshold",
                         help="threshold: 四隅の色による閾値方式。grabcut: 背景に物が写り込む場合向け。"
                              "gradient: 背景に照明のグラデーションがある場合向け")
    parser.add_argument("--remove-shadow", action="store_true",
                         help="gradient方式で床の影を除去する（無彩色の服では内部に穴が開く副作用があるため既定は無効）")
    args = parser.parse_args()

    image = cv2.imread(args.input)
    if image is None:
        raise FileNotFoundError(f"画像を読み込めませんでした: {args.input}")

    if args.method == "grabcut":
        mask = extract_silhouette_grabcut(image)
    elif args.method == "gradient":
        mask = extract_silhouette_gradient(image, args.threshold, remove_shadow=args.remove_shadow)
    else:
        mask = extract_silhouette(image, args.threshold)
    cv2.imwrite(args.output, mask)
    covered = int((mask > 0).sum())
    total = mask.size
    print(f"foreground pixels: {covered} / {total} ({covered / total:.1%})")


if __name__ == "__main__":
    main()
