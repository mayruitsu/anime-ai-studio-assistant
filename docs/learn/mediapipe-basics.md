# MediaPipe基礎学習メモ

## MediaPipeとは

Googleが開発した機械学習ライブラリ。カメラや画像から「人・手・顔」などを検出する処理がすぐ使える。
このプロジェクトでは **Pose（姿勢推定）** モジュールを使い、人型画像から関節33点の座標を検出する。

## import と初期設定

```python
import mediapipe as mp
mp_pose = mp.solutions.pose
```

- `mp.solutions.pose` で Pose 検出モジュールを取得する

## Pose クラスと画像処理

```python
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

with mp_pose.Pose(static_image_mode=True) as pose:
    results = pose.process(image_rgb)
```

- OpenCV は BGR 順で読み込むが、MediaPipe は RGB を期待するため変換が必要
- `static_image_mode=True` は静止画用（毎回フルで検出・精度重視）
- `with` 構文でモデルを使い終わったら自動でリソースを解放する

## 検出結果の読み方

```python
results.pose_landmarks.landmark[i]
```

- `results.pose_landmarks` が `None` なら人物が検出されなかった
- `.landmark` は33点のリスト（インデックス0〜32）
- 座標は **画像サイズに対する比率（0〜1）** で返る

| 属性 | 意味 |
|---|---|
| `x` / `y` | 横・縦位置（0.0〜1.0） |
| `z` | 奥行き（相対値） |
| `visibility` | 見えているか（0.0〜1.0） |

ピクセル値に直すには画像の幅・高さをかける。

```python
px = int(landmark.x * image_width)
py = int(landmark.y * image_height)
```

## 主要な関節インデックス

| インデックス | 部位 |
|---|---|
| 0 | 鼻 |
| 11 / 12 | 左肩 / 右肩 |
| 13 / 14 | 左肘 / 右肘 |
| 15 / 16 | 左手首 / 右手首 |
| 23 / 24 | 左腰 / 右腰 |
| 25 / 26 | 左膝 / 右膝 |
| 27 / 28 | 左足首 / 右足首 |
