import sys
import cv2
import mediapipe as mp
import numpy as np

mp_selfie_segmentation = mp.solutions.selfie_segmentation


def segment_person(image_path: str):
    image = cv2.imread(image_path)
    if image is None:
        print(f"画像を読み込めませんでした: {image_path}")
        return

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp_selfie_segmentation.SelfieSegmentation(model_selection=0) as segmenter:
        results = segmenter.process(image_rgb)

    mask = (results.segmentation_mask > 0.5).astype(np.uint8) * 255
    person_ratio = (mask > 0).mean() * 100
    print(f"人物切り抜き成功: 画像中の人物領域は約{person_ratio:.1f}%")

    output_path = "mask_output.png"
    cv2.imwrite(output_path, mask)
    print(f"マスク画像を保存しました: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python segmentation_test.py <画像ファイルパス>")
    else:
        segment_person(sys.argv[1])