# MediaRecorder / captureStream 基礎学習メモ

## やりたいこと

Three.jsで描画している`<canvas>`の内容を、そのまま動画ファイル（webm）として書き出したい。サーバー側でのレンダリングやOpenCVでの動画合成は使わず、ブラウザだけで完結させる。

## canvas.captureStream()

`<canvas>`要素は`captureStream(fps)`で、その描画内容を`MediaStream`（映像ストリーム）として取り出せる。

```js
const stream = canvas.captureStream(10); // 10fpsでキャプチャ
```

fpsを低くすると、アニメの2コマ・3コマ打ちのような「あえてカクつかせた」動画になる。

## MediaRecorder

`MediaStream`を受け取って録画するAPI。

```js
const recorder = new MediaRecorder(stream, { mimeType: "video/webm" });
const chunks = [];
recorder.ondataavailable = (e) => chunks.push(e.data);
recorder.start();
// ... この間にcanvasの中身（VRMのポーズ）を変化させる ...
recorder.stop();
```

`recorder.onstop`が呼ばれた時点で`chunks`に録画データが溜まっている。`Blob`にまとめて`URL.createObjectURL`でダウンロードリンクを作れる。

## ポイント

- キャプチャは「今canvasに描画されているもの」をそのまま撮るだけなので、録画中に見た目を変えたければ、録画開始後にボーンの回転などを実際に変更する必要がある
- `await new Promise((r) => setTimeout(r, ms))`でポーズ変更の間隔を空けることで、アニメ的なタイミングを作れる
