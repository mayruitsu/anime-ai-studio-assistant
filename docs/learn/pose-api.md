# ポーズ検出API 解説

## 使用ライブラリとその役割

| ライブラリ | 役割 |
|---|---|
| `mediapipe` | 画像から関節33点を検出するAI |
| `opencv-python` | 画像の読み込み・色変換 |
| `numpy` | バイト列を画像データ（数値配列）に変換 |
| `python-multipart` | ファイルアップロードを扱うために必要 |

## ファイル構成

```
main.py   ← ルーティング（URLと関数の対応づけ）
pose.py   ← 検出ロジック（実際の画像処理）
```

## pose.py の処理の流れ

```
bytes（アップロードファイルの生データ）
  ↓ np.frombuffer()   バイト列 → numpy配列
  ↓ cv2.imdecode()    numpy配列 → 画像データ
  ↓ cv2.cvtColor()    BGR → RGB に変換
  ↓ pose.process()    AIで関節座標を計算
  ↓ return            33点のリストを返す
```

## 学習ポイント

**`np.frombuffer(image_bytes, np.uint8)`**
ファイルの生バイト列を numpy 配列に変換する。`np.uint8` は 0〜255 の整数型でピクセルの輝度値に対応する。

**`async def` と `await`**
`async def` は非同期関数の定義。`await file.read()` でファイルの読み込み完了を待つ。FastAPI のエンドポイントでは `async def` を使うのが基本。

**`list[dict] | None`（戻り値の型ヒント）**
`None` は画像の読み込み失敗、`list[dict]` は正常時の33点リストを表す。`| None` は Python 3.10 以降の書き方。
