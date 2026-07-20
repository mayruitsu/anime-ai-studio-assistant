import sys
import cv2

from pose import detect_pose
from segmentation import segment_person
from part_cropping import crop_parts
from rotation import calc_rotation_angles, calc_scales
from render import render_frame


def main(image_path: str):
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    base_points = detect_pose(image_bytes)
    if not base_points:
        print("関節ポイントが検出されませんでした")
        return

    mask_bytes = segment_person(image_bytes)
    if mask_bytes is None:
        print("人物切り抜きに失敗しました")
        return

    parts = crop_parts(image_bytes, mask_bytes, base_points)
    image = cv2.imread(image_path)
    height, width = image.shape[:2]
    # 左肘（13）を大きく曲げてみる動作確認用のポーズ
    target_points = [dict(p) for p in base_points]
    elbow = target_points[13]
    target_points[13] = {**elbow, "x": elbow["x"] - 0.05, "y": elbow["y"] + 0.15}

    angles = calc_rotation_angles(base_points, target_points)
    scales = calc_scales(base_points, target_points)
    frame = render_frame(parts, angles, scales, target_points, (width, height))
    cv2.imwrite("render_output.png", frame)
    print("render_output.png に保存しました")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python render_test.py <画像ファイルパス>")
    else:
        main(sys.argv[1])
