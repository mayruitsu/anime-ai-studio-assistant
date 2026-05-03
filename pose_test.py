import sys
import cv2
import mediapipe as mp

mp_pose = mp.solutions.pose


def detect_pose(image_path: str):
    image = cv2.imread(image_path)
    if image is None:
        print(f"画像を読み込めませんでした: {image_path}")
        return

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(image_rgb)

    if results.pose_landmarks:
        print(f"関節ポイント検出成功: {len(results.pose_landmarks.landmark)}点")
        for i, landmark in enumerate(results.pose_landmarks.landmark):
            print(f"  [{i:02d}] x={landmark.x:.3f}, y={landmark.y:.3f}, z={landmark.z:.3f}")
    else:
        print("関節ポイントが検出されませんでした（人物が映っていない可能性があります）")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ライブラリ読み込み確認:")
        print(f"  mediapipe: {mp.__version__}")
        print(f"  opencv:    {cv2.__version__}")
        print()
        print("使い方: python pose_test.py <画像ファイルパス>")
    else:
        detect_pose(sys.argv[1])
