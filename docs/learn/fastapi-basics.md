# FastAPI基礎学習メモ

## import について

```python
from fastapi import FastAPI
```

- fastapiライブラリの中にある `FastAPI` という設計図（クラス）をこのファイルに持ってくる
- Pythonはファイルをまたいで自動共有されないので、使いたいファイルごとに `import` を書く必要がある
- ライブラリ = 「よく使う処理をまとめて誰でも使いやすくしたコードの集まり」。自前でクラスを書かなくて済む

## クラスとインスタンス

- **クラス** = 設計図
- **インスタンス** = 設計図から作った実体

```python
# クラスの例（たい焼きの型）
class Taiyaki:
    def __init__(self, filling):
        self.filling = filling

# インスタンスの例（実際に焼いたたい焼き）
a = Taiyaki("あんこ")
b = Taiyaki("クリーム")
```

- Pythonの慣習でクラスは大文字始まり（`FastAPI`）、関数は小文字始まり（`print`）で書く
- この慣習でクラスか関数かを見分けられる

## app = FastAPI()

```python
app = FastAPI()
```

- `FastAPI`（クラス）からインスタンスを作って `app` という変数に入れている
- 「FastAPIアプリを1つ作って、`app` と名付けた」というイメージ
- 必要な理由は2つ：
  1. `@app.get(...)` のようにURLを登録する起点になる
  2. `uvicorn main:app` でuvicornに渡す実体になる

## def について

```python
def health():
    return {"status": "ok"}
```

- `def` がついているものが関数
- `def` がない `()` は関数呼び出しかインスタンス生成

| 書き方 | 何か |
|---|---|
| `def xxx():` | 関数の定義 |
| `クラス名()` | インスタンス生成 |
| `関数名()` | 関数呼び出し |

## デコレータ

```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

- `@` がデコレータの印
- 「`/health` にGETリクエストが来たら直下の関数を実行してね」と `app` に登録している
- URLのパス（`/health`）と関数名（`health`）はたまたま同じなだけで別物。関数名は何でもいい

## HTTPメソッド

| メソッド | いつ来るか | 用途 |
|---|---|---|
| GET | ブラウザでURLを開く | データの取得 |
| POST | フォーム送信・ボタン押下 | データの送信・作成 |
| PUT | 編集フォームの保存 | データの更新 |
| DELETE | 削除ボタン押下 | データの削除 |

- ブラウザにURLを入力してEnterを押す = GETリクエストを送る
