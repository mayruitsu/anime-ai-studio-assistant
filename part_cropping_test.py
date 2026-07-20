import sys
import cv2

from pose import detect_pose
from segmentation import segment_person
from part_cropping import crop_parts


def main(image_path: str):
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    landmarks = detect_pose(image_bytes)
    if not landmarks:
        print("関節ポイントが検出されませんでした")
        return

    mask_bytes = segment_person(image_bytes)
    if mask_bytes is None:
        print("人物切り抜きに失敗しました")
        return

    parts = crop_parts(image_bytes, mask_bytes, landmarks)

    for name, part in parts.items():
        output_path = f"part_{name}.png"
        cv2.imwrite(output_path, part["image"])
        print(f"{name}: {output_path} に保存しました（pivot_offset={part['pivot_offset']}）")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python part_cropping_test.py <画像ファイルパス>")
    else:
        main(sys.argv[1])
