# MediaPipe Poseの関節33点（pose.py参照）を、剛体として動かすパーツ単位にグルーピングする対応表。
# 各パーツは (付け根の関節, 先端の関節) のペアで表し、pivot は回転の軸となる付け根側の関節インデックス。
BODY_PARTS = {
    "head": {"joints": (11, 0), "pivot": 11},
    "torso": {"joints": (11, 23), "pivot": 11},
    "upper_arm_left": {"joints": (11, 13), "pivot": 11},
    "forearm_left": {"joints": (13, 15), "pivot": 13},
    "upper_arm_right": {"joints": (12, 14), "pivot": 12},
    "forearm_right": {"joints": (14, 16), "pivot": 14},
    "thigh_left": {"joints": (23, 25), "pivot": 23},
    "shin_left": {"joints": (25, 27), "pivot": 25},
    "thigh_right": {"joints": (24, 26), "pivot": 24},
    "shin_right": {"joints": (26, 28), "pivot": 26},
}

# レンダリング時の描画順（奥から手前）。脚→胴体→腕→頭の順に重ねる。
DRAW_ORDER = [
    "shin_left", "shin_right", "thigh_left", "thigh_right", "torso",
    "upper_arm_left", "upper_arm_right", "forearm_left", "forearm_right", "head",
]

# 複数写真から選ぶ際、このグループ単位で同じ写真を使う（隣接パーツが別写真になり継ぎ目が
# 目立つのを防ぐ。例：スカートは両脚まとめて同じ写真から選ぶ）
PART_GROUPS = [
    ["head"],
    ["torso"],
    ["upper_arm_left", "forearm_left"],
    ["upper_arm_right", "forearm_right"],
    ["thigh_left", "shin_left", "thigh_right", "shin_right"],
]