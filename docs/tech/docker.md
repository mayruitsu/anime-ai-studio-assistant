# Docker

## Dockerとは

アプリケーションとその実行環境をまとめて「コンテナ」として管理するツール。
「自分のPCでは動くのに本番では動かない」という問題を防ぐ。

## このプロジェクトでの使い方

| ファイル | 役割 |
|---|---|
| `Dockerfile` | コンテナの構成定義（本番・ローカル共通） |
| `docker-compose.yml` | ローカル開発用の起動設定 |
| `.env.local` | ローカル環境変数（gitignore対象） |
| `.env.example` | 環境変数のテンプレート |

## 環境の切り替え

環境変数 `ENV` の値でローカルと本番を判別する。

- ローカル：`docker-compose.yml` が `.env.local` を読み込む
- 本番（Cloud Run）：GCP側で環境変数を設定する

## よく使うコマンド

```bash
# 起動
docker compose up

# バックグラウンド起動
docker compose up -d

# 停止
docker compose down

# イメージ再ビルド
docker compose up --build
```

## Dockerfile の読み方

```dockerfile
FROM python:3.11-slim        # ベースイメージ（Python 3.11）
WORKDIR /app                 # 作業ディレクトリ
COPY requirements.txt .      # 依存ファイルをコピー
RUN pip install ...          # ライブラリをインストール
COPY . .                     # ソースコードをコピー
CMD ["uvicorn", ...]         # 起動コマンド
```
