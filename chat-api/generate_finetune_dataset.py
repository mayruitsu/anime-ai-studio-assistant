"""OLMoのファインチューニング用対話データを、テンプレートから合成生成する。

self-model-experimentの骨格編集モデル（generate_skeleton_edit_dataset.py）と同じ発想：
テキスト→構造化出力（ツール呼び出しJSON）のペアを、テンプレートの組み合わせで
自動生成する。実際のユーザー対話ログは使わない（学習データの出処を完全に自己管理するため）。
"""
import argparse
import json
import random

from tools import format_tools_for_prompt

BONE_NAMES_JA = {
    "head": "頭", "neck": "首", "chest": "胸", "spine": "背骨", "hips": "腰",
    "leftUpperArm": "左上腕", "leftLowerArm": "左前腕", "leftHand": "左手",
    "rightUpperArm": "右上腕", "rightLowerArm": "右前腕", "rightHand": "右手",
    "leftUpperLeg": "左太もも", "leftLowerLeg": "左すね", "leftFoot": "左足",
    "rightUpperLeg": "右太もも", "rightLowerLeg": "右すね", "rightFoot": "右足",
}
AXES_JA = {"x": "縦", "y": "横", "z": "ひねり"}
MOTION_PROMPTS = ["a person walks forward", "a person waves hello", "a person jumps",
                  "a person sits down", "a person runs", "a person bows"]
SYSTEM_PROMPT = format_tools_for_prompt()


def _example(user_text: str, tool: str, params: dict) -> dict:
    return {"messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": json.dumps({"tool": tool, "params": params}, ensure_ascii=False)},
    ]}


def generate_examples(seed: int = 0) -> list:
    rng = random.Random(seed)
    examples = []

    for phrase in ["今のポーズを教えて", "現在の姿勢を確認して", "今どんなポーズになってる？", "ポーズの状態を見せて"]:
        examples.append(_example(phrase, "get_current_pose", {}))

    for bone, bone_ja in BONE_NAMES_JA.items():
        for axis, axis_ja in AXES_JA.items():
            amount = rng.choice([0.2, 0.5, 0.8, 1.0, 1.3])
            params = {"bone_name": bone, "x": 0.0, "y": 0.0, "z": 0.0}
            params[axis] = amount
            examples.append(_example(f"{bone_ja}を{axis_ja}方向に少し回転させて", "set_bone_rotation", params))

    for phrase in ["今のポーズをキーフレームに追加して", "この姿勢を記録して", "現在の姿勢を保存して"]:
        examples.append(_example(phrase, "add_keyframe", {}))
    for phrase in ["キーフレームを全部消して", "記録をリセットして", "キーフレームをクリアして"]:
        examples.append(_example(phrase, "clear_keyframes", {}))
    for phrase in ["動画を書き出して", "アニメーションを保存して", "今までのキーフレームを動画にして"]:
        examples.append(_example(phrase, "export_keyframe_video", {}))

    for i in range(5):
        url = f"https://example.com/models/avatar{i}.vrm"
        examples.append(_example(f"{url}のモデルを読み込んで", "load_vrm_model", {"url": url}))

    for prompt in MOTION_PROMPTS:
        examples.append(_example(f"「{prompt}」という動きを生成して", "start_motion_generation", {"prompt": prompt}))

    for i in range(5):
        job_id = f"job-{i:03d}"
        examples.append(_example(f"さっき頼んだモーション生成できた？(job_id: {job_id})",
                                  "get_motion_generation_status", {"job_id": job_id}))
        examples.append(_example(f"{job_id}のモーションを再生して動画にして",
                                  "play_and_export_generated_motion", {"job_id": job_id}))

    rng.shuffle(examples)
    return examples


def main():
    parser = argparse.ArgumentParser(description="ファインチューニング用対話データをJSONL形式で生成する")
    parser.add_argument("output_path")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    examples = generate_examples(args.seed)
    with open(args.output_path, "w", encoding="utf-8") as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")
    print(f"{len(examples)}件の対話データを{args.output_path}に書き出しました")


if __name__ == "__main__":
    main()
