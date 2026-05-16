# フロントエンド・API連携 解説

## CORS とは

ブラウザはセキュリティ上、**異なるポートへのリクエストをデフォルトで拒否**する。
フロント（`:5173`）からAPI（`:8080`）への通信がこれに該当するため、API側に許可設定が必要。

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## FormData とは

ファイルをAPIに送るための入れ物。`<form>` タグでのファイル送信をJSで再現する。

```js
const formData = new FormData();
formData.append("file", file);  // "file" はAPIの引数名と一致させる
```

## fetch と async/await

```js
const res = await fetch("http://localhost:8080/detect-pose", {
    method: "POST",
    body: formData,
});
const data = await res.json();
```

- `async` ── 非同期処理を含む関数の宣言
- `await fetch(...)` ── レスポンスが届くまで待つ
- `await res.json()` ── JSONの変換が終わるまで待つ

## 処理の流れ

```
画像を選択
  ↓ setImage(url)       Canvas に画像を表示
  ↓ FormData に file    APIに送る準備
  ↓ fetch でAPI呼び出し・待機
  ↓ 33点を受け取る
  ↓ setFrames([points]) Canvas のポイントを更新
```
