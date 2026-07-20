import sys
import cv2

from multi_photo import build_photo_profiles, select_parts_for_pose
from render import render_frame


def _interpolate(a: list[dict], b: list[dict], t: float) -> list[dict]:
    return [
        {"x": pa["x"] + (pb["x"] - pa["x"]) * t, "y": pa["y"] + (pb["y"] - pa["y"]) * t}
        for pa, pb in zip(a, b)
    ]


def main(image_paths: list[str], frame_count: int):
    photos = []
    for path in image_paths:
        with open(path, "rb") as f:
            photos.append(f.read())

    profiles = build_photo_profiles(photos)
    if not profiles:
        print("ポーズ検出できた写真がありません")
        return

    start_pose = profiles[0]["base_points"]
    end_pose = profiles[-1]["base_points"]

    image = cv2.imread(image_paths[0])
    height, width = image.shape[:2]

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter("multi_photo_output.mp4", fourcc, 10, (width, height))

    for i in range(frame_count):
        t = i / (frame_count - 1)
        target_points = _interpolate(start_pose, end_pose, t)
        parts, angles, scales = select_parts_for_pose(profiles, target_points)
        frame = render_frame(parts, angles, scales, target_points, (width, height))
        out.write(frame)
        if i in (0, frame_count // 2, frame_count - 1):
            cv2.imwrite(f"multi_photo_frame_{i}.png", frame)

    out.release()
    print(f"multi_photo_output.mp4 に保存しました（フレーム数: {frame_count}、写真数: {len(profiles)}）")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python multi_photo_test.py <画像1> [<画像2> ...] [フレーム数]")
    else:
        args = sys.argv[1:]
        frame_count = 30
        if args[-1].isdigit():
            frame_count = int(args.pop())
        main(args, frame_count)
