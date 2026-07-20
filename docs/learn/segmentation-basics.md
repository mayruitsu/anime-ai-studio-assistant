# 人物切り抜き（セグメンテーション）基礎学習メモ

## Selfie Segmentationとは

MediaPipeが提供する、画像から「人物か背景か」をピクセル単位で判定するモデル。姿勢推定（Pose）とは別のモジュールだが、使い方の流れはよく似ている。

```python
import mediapipe as mp
mp_selfie_segmentation = mp.solutions.selfie_segmentation
```

## Poseとの違い

| | Pose | Selfie Segmentation |
|---|---|---|
| 返すもの | 関節33点の座標 | 画像と同じ大きさのマスク（人物らしさの値） |
| 用途 | 骨格・ポーズの把握 | 人物と背景の分離 |

## 使い方

```python
with mp_selfie_segmentation.SelfieSegmentation(model_selection=0) as segmenter:
    results = segmenter.process(image_rgb)

mask = results.segmentation_mask
```

- `model_selection=0`：一般的な用途向けモデル（1は近距離・上半身向けモデル）
- `results.segmentation_mask` は画像と同じ縦横サイズの配列で、各ピクセルに「人物らしさ」が **0.0〜1.0の連続値** で入っている（Poseの`visibility`と似た考え方）

## マスクの2値化

連続値のままだと扱いにくいので、しきい値で「人物 / 背景」の2値に変換する。

```python
mask = (results.segmentation_mask > 0.5).astype(np.uint8) * 255
```

- `> 0.5` で人物と判定されたピクセルを`True`にする
- `* 255` でグレースケール画像として保存できる値（0または255）にする

## 今回の設計判断

- エンドポイントはマスク画像（PNG、1チャンネル）そのものを返す。人物を切り抜いた画像（透明背景など）は返さない
- 理由：次のステップ（パーツ画像の切り出し）で「マスク＋関節点の対応表」を組み合わせてパーツごとに切り出す予定のため、この段階では素材となるマスクだけを渡せば十分