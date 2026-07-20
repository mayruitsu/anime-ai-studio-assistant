import sys
import cv2
import numpy as np

from illustration_segmentation import segment_by_background_color


def main(image_path: str):
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    mask_bytes = segment_by_background_color(image_bytes)
    if mask_bytes is None:
        print("画像の読み込みに失敗しました")
        return

    mask = cv2.imdecode(np.frombuffer(mask_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)
    person_ratio = (mask > 0).mean() * 100

    output_path = "illustration_mask_output.png"
    with open(output_path, "wb") as f:
        f.write(mask_bytes)

    print(f"背景色ベースの切り抜き成功: 人物領域は約{person_ratio:.1f}%")
    print(f"マスク画像を保存しました: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python illustration_segmentation_test.py <画像ファイルパス>")
    else:
        main(sys.argv[1])
