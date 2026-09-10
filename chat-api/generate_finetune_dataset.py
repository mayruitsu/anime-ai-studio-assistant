"""OLMoのファインチューニング用対話データを、テンプレートから合成生成する。

self-model-experimentの骨格編集モデル（generate_skeleton_edit_dataset.py）と同じ発想：
テキスト→構造化出力（ツール呼び出しJSON）のペアを、テンプレートの組み合わせで
自動生成する。実際のユーザー対話ログは使わない（学習データの出処を完全に自己管理するため）。
"""
import argparse
import json
import random

from tools import format_tools_for_prompt

# VRM humanoidの指ボーン（親指のみMetacarpal始まり、他はProximal始まり）を機械的に生成する。
# 手打ちすると量が多くタイプミスの元になるため、対応表からループで組み立てる
_FINGER_JOINTS_JA = {"Metacarpal": "の付け根", "Proximal": "の根元", "Intermediate": "の第二関節", "Distal": "の先"}
_FINGER_JOINT_ORDER = {
    "Thumb": ["Metacarpal", "Proximal", "Distal"],
    "Index": ["Proximal", "Intermediate", "Distal"],
    "Middle": ["Proximal", "Intermediate", "Distal"],
    "Ring": ["Proximal", "Intermediate", "Distal"],
    "Little": ["Proximal", "Intermediate", "Distal"],
}
_FINGERS_JA = {"Thumb": "親指", "Index": "人差し指", "Middle": "中指", "Ring": "薬指", "Little": "小指"}


def _finger_bone_names_ja() -> dict:
    names = {}
    for side, side_ja in [("left", "左"), ("right", "右")]:
        for finger, finger_ja in _FINGERS_JA.items():
            for joint in _FINGER_JOINT_ORDER[finger]:
                names[f"{side}{finger}{joint}"] = f"{side_ja}{finger_ja}{_FINGER_JOINTS_JA[joint]}"
    return names


BONE_NAMES_JA = {
    "head": "頭", "neck": "首", "chest": "胸", "upperChest": "上胸", "spine": "背骨", "hips": "腰",
    "jaw": "あご", "leftEye": "左目", "rightEye": "右目",
    "leftShoulder": "左肩甲骨", "rightShoulder": "右肩甲骨",
    "leftUpperArm": "左上腕", "leftLowerArm": "左前腕", "leftHand": "左手",
    "rightUpperArm": "右上腕", "rightLowerArm": "右前腕", "rightHand": "右手",
    "leftUpperLeg": "左太もも", "leftLowerLeg": "左すね", "leftFoot": "左足", "leftToes": "左つま先",
    "rightUpperLeg": "右太もも", "rightLowerLeg": "右すね", "rightFoot": "右足", "rightToes": "右つま先",
    **_finger_bone_names_ja(),
}
AXES_JA = {"x": "縦", "y": "横", "z": "ひねり"}
# 「少し」等のあいまいな表現に対し、対応する角度をランダムではなく固定値にする。
# ランダムにすると同じ表現に毎回違う正解を割り当てることになり、モデルが学習できない
AMOUNT_PHRASES = [("少し", 0.3), ("そこそこ", 0.7), ("大きく", 1.2)]
MOTION_PROMPTS = ["a person walks forward", "a person waves hello", "a person jumps",
                  "a person sits down", "a person runs", "a person bows"]
SYSTEM_PROMPT = format_tools_for_prompt()

# 「もう少し」等、前回の自分の指示を踏まえた相対的な追加指示のバリエーション。
# 増分は固定値（0.3）にする。ランダムにすると同じ表現に毎回違う正解が付き学習できなくなる
RELATIVE_MORE_PHRASES = ["もっと動かして", "もう少しお願い", "さらに回転させて", "もう少し動かして"]
RELATIVE_RESET_PHRASES = ["元に戻して", "さっきの回転をリセットして", "元の姿勢に戻して", "戻して"]
RELATIVE_MORE_INCREMENT = 0.3


def _example(user_text: str, tool: str, params: dict) -> dict:
    return {"messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": json.dumps({"tool": tool, "params": params}, ensure_ascii=False)},
    ]}


def _multi_turn_example(turns: list) -> dict:
    """turns: [(ユーザーの発話, tool, params), ...] を1つの会話にまとめる。
    最後のツール呼び出しのみが学習対象（finetune_olmo.pyのマスキング）になるが、
    それより前のやり取りは文脈として与えられる（「もう少し」のような相対指示が
    直前の自分の出力を参照できるようにするため）。
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for user_text, tool, params in turns:
        messages.append({"role": "user", "content": user_text})
        messages.append({"role": "assistant", "content": json.dumps({"tool": tool, "params": params}, ensure_ascii=False)})
    return {"messages": messages}


def generate_relative_adjustment_examples(rng) -> list:
    """「(関節)を回転させて」の後に「もっと」「元に戻して」と続く2ターンの会話例。

    直前の自分の出力（同じ関節・軸への回転）を踏まえて、次の指示に正しく答えられるかを
    学習させる。会話履歴には直前のツール呼び出しの生JSONがそのまま積まれる前提
    （フロントエンドのChatBox.jsx参照）。
    """
    examples = []
    for bone, bone_ja in BONE_NAMES_JA.items():
        for axis, axis_ja in AXES_JA.items():
            first_text = f"{bone_ja}を{axis_ja}方向に少し回転させて"
            first_params = {"bone_name": bone, "x": 0.0, "y": 0.0, "z": 0.0}
            first_params[axis] = 0.3

            more_params = dict(first_params)
            more_params[axis] = round(0.3 + RELATIVE_MORE_INCREMENT, 2)
            examples.append(_multi_turn_example([
                (first_text, "set_bone_rotation", first_params),
                (rng.choice(RELATIVE_MORE_PHRASES), "set_bone_rotation", more_params),
            ]))

            reset_params = {"bone_name": bone, "x": 0.0, "y": 0.0, "z": 0.0}
            examples.append(_multi_turn_example([
                (first_text, "set_bone_rotation", first_params),
                (rng.choice(RELATIVE_RESET_PHRASES), "set_bone_rotation", reset_params),
            ]))
    return examples


def generate_examples(seed: int = 0) -> list:
    rng = random.Random(seed)
    examples = []

    for phrase in ["今のポーズを教えて", "現在の姿勢を確認して", "今どんなポーズになってる？", "ポーズの状態を見せて"]:
        examples.append(_example(phrase, "get_current_pose", {}))

    for bone, bone_ja in BONE_NAMES_JA.items():
        for axis, axis_ja in AXES_JA.items():
            amount_phrase, amount = rng.choice(AMOUNT_PHRASES)
            params = {"bone_name": bone, "x": 0.0, "y": 0.0, "z": 0.0}
            params[axis] = amount
            examples.append(_example(f"{bone_ja}を{axis_ja}方向に{amount_phrase}回転させて", "set_bone_rotation", params))

    examples.extend(generate_relative_adjustment_examples(rng))

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
