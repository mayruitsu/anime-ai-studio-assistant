import sys
import cv2

from pose import detect_pose
from video import generate_video


def main(image_path: str):
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    base_points = detect_pose(image_bytes)
    if not base_points:
        print("関節ポイントが検出されませんでした")
        return

    target_points = [dict(p) for p in base_points]
    elbow = target_points[13]
    target_points[13] = {**elbow, "x": elbow["x"] - 0.05, "y": elbow["y"] + 0.15}

    video_bytes = generate_video(image_bytes, [base_points, target_points])
    with open("video_output.mp4", "wb") as f:
        f.write(video_bytes)

    cap = cv2.VideoCapture("video_output.mp4")
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    ok, last_frame = None, None
    for _ in range(frame_count):
        ok, last_frame = cap.read()
    if ok:
        cv2.imwrite("video_last_frame.png", last_frame)
    cap.release()

    print(f"video_output.mp4 に保存しました（フレーム数: {frame_count}）")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python video_test.py <画像ファイルパス>")
    else:
        main(sys.argv[1])
