# ポーズ検出API 解説

## 使用ライブラリとその役割

| ライブラリ | 役割 |
|---|---|
| `mediapipe` | 画像から関節33点を検出するAI |
| `opencv-python` | 画像の読み込み・色変換 |
| `numpy` | バイト列を画像データ（数値配列）に変換 |
| `fastapi` | HTTPリクエストを受け取るWebフレームワーク |
| `python-multipart` | ファイルアップロードを扱うために必要 |

## ファイル構成

```
main.py   ← ルーティング（どのURLで何をするか）
pose.py   ← 検出ロジック（実際の画像処理）
```

責務を分けることで、main.py はURLの定義だけに集中できる。

## pose.py の処理の流れ

```
bytes（画像ファイルの生データ）
  ↓ np.frombuffer()   バイト列 → numpy配列
  ↓ cv2.imdecode()    numpy配列 → 画像データ（ピクセル）
  ↓ cv2.cvtColor()    BGR → RGB に変換
  ↓ pose.process()    AIで関節座標を計算
  ↓ return            33点のリストを返す
```

## 重要な関数・クラスの説明

### `np.frombuffer(image_bytes, np.uint8)`
ファイルの生バイト列（`bytes`型）を numpy の数値配列に変換する。
`np.uint8` は「0〜255の整数」を意味し、ピクセルの輝度値の型に合わせている。

### `cv2.imdecode(nparr, cv2.IMREAD_COLOR)`
numpy配列を OpenCV が扱える画像データに変換する。
`IMREAD_COLOR` はカラー（BGR3チャンネル）で読み込む指定。

### `list[dict] | None` （戻り値の型ヒント）
- `list[dict]` ── 正常時、33点の辞書リスト
- `None` ── 画像の読み込み失敗時

`| None` は「Noneになることもある」という意味（Python 3.10以降の書き方）。

## main.py の処理の流れ

```
POST /detect-pose にリクエスト
  ↓ file.read()         アップロードされたファイルをバイト列で受け取る
  ↓ detect_pose()       pose.py の関数に渡す
  ↓ landmarks is None   画像読み込み失敗 → 400エラーを返す
  ↓ return              {"landmarks": [...]} を返す
```

## 学習ポイント

**`async def` と `await` について**
`async def` は「非同期関数」の定義。`await file.read()` の `await` は
「ファイルの読み込みが終わるまで待つ」という意味。
FastAPI のエンドポイントでは `async def` を使うのが基本。

**`HTTPException` について**
エラー時に適切なHTTPステータスコードをクライアントに返すための仕組み。
`status_code=400` は「リクエストが不正」を意味する。
