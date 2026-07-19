# 動画出力 解説

## 使用ライブラリとその役割

| ライブラリ | 役割 |
|---|---|
| `cv2.VideoWriter` | フレームを順に書き込んで動画ファイルを生成する |
| `tempfile` | OS の一時ディレクトリに使い捨てのファイルを作成する |
| `os.unlink` | 指定したファイルを削除する |
| `numpy` | 画像データの数値配列処理（imdecode 内部で使用） |

## コードの処理の流れ

```
画像バイト列（image_bytes）
  ↓ np.frombuffer + cv2.imdecode   バイト列 → 画像データ
  ↓ image.shape[:2]                画像の高さ・幅を取得

tempfile で一時ファイルパスを確保
  ↓ cv2.VideoWriter                動画ファイルの書き込み準備

各フレームでループ
  ↓ image.copy()                   元画像を複製
  ↓ cv2.circle() × 33回           関節ポイントを赤丸で描画
  ↓ out.write(frame)               1フレームを動画に追加

out.release()                      動画ファイルを確定・保存
  ↓ open(tmp_path, "rb").read()    ファイルをバイト列として読み込む
  ↓ os.unlink(tmp_path)            一時ファイルを削除
  ↓ return video_bytes             動画バイト列を返す
```

## 重要な関数・クラスの説明

### `cv2.VideoWriter_fourcc(*"mp4v")`

動画の圧縮形式（コーデック）を指定する。
`"mp4v"` は MP4 形式でよく使われるコーデック。

```python
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
# *"mp4v" は ("m", "p", "4", "v") と同じ意味（文字列をバラして渡す）
```

### `cv2.VideoWriter(path, fourcc, fps, (w, h))`

動画ファイルへの書き込みオブジェクトを作る。

| 引数 | 意味 |
|---|---|
| `path` | 書き出し先のファイルパス |
| `fourcc` | コーデック |
| `fps` | 1秒あたりのフレーム数 |
| `(w, h)` | 動画の解像度（幅・高さ） |

### `cv2.circle(frame, (px, py), 6, (0, 0, 255), -1)`

画像に円を描画する。

| 引数 | 意味 |
|---|---|
| `frame` | 描画先の画像 |
| `(px, py)` | 円の中心座標（ピクセル） |
| `6` | 半径（ピクセル） |
| `(0, 0, 255)` | 色（BGR形式 → 赤） |
| `-1` | 塗りつぶし（正の値なら線の太さ） |

座標は比率（0〜1）なので、画像サイズをかけてピクセル値に変換している。

```python
px = int(point["x"] * w)
py = int(point["y"] * h)
```

## 学習ポイント

**`image.copy()` が必要な理由**

```python
for frame_points in frames:
    frame = image.copy()  # ← ここ
    for point in frame_points:
        cv2.circle(frame, ...)  # frame に描画
    out.write(frame)
```

`image` をそのまま使うと `cv2.circle()` が元画像を直接書き換えてしまい、次のフレームでも前フレームの丸が残り続ける。`copy()` でフレームごとに新しいコピーを作ることで、毎回クリーンな元画像から描き始められる。

**`tempfile` を使う理由**

`cv2.VideoWriter` は「ファイルパスに書き出す」仕組みで、メモリに直接書き出す方法がない。そのため：

1. 一時ファイルに書き出す（`tmp_path`）
2. 書き終わったらバイト列として読み込む
3. 一時ファイルを削除（`os.unlink`）

という手順を踏む必要がある。

**`out.release()` を忘れると**

動画ファイルが正しく閉じられず、再生できない壊れたファイルになる。`VideoWriter` を使い終わったら必ず `release()` を呼ぶ。
