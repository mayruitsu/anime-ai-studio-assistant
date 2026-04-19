# アニメーションアシスタントAI

1枚の人型画像から関節ポイントを自動検出し、ユーザーがフレームごとに操作してアニメーションを作成するアシスタントツール。

---

## 開発ルール

### ブランチ
- `main` への直接pushは禁止。必ずブランチを作成してPR経由でマージする
- ブランチ名には必ず連番を付ける（mainから派生した最初のブランチを `01` とする）
- 命名形式：`feature/01-topic`、`learn/01-topic`

### PR
- 1PRの差分は削除を含めて **100行以内** を目安にする
- PRのタイトルは **日本語** で記載する

### ドキュメント
- PR作成時にGitHub Actionsが自動でコード解説を `docs/pr-notes/` に生成する
- 学習メモは `docs/learn/` に手動で残す

---

## ディレクトリ構成

```
docs/
  learn/       # 学習メモ
  pr-notes/    # PRごとの自動コード解説
.github/
  workflows/   # GitHub Actions
```

---

## 技術スタック

### AI・バックエンド

| 技術 | 用途 |
|---|---|
| MediaPipe Pose | 人型画像からの関節ポイント自動検出 |
| Python + FastAPI | APIサーバー |
| OpenCV | アニメーション動画の出力 |

### フロントエンドUI

| 技術 | 用途 |
|---|---|
| React | UIフレームワーク |
| Canvas API | フレームごとのポイント操作・描画 |

### インフラ

| 技術 | 用途 |
|---|---|
| GCP Cloud Run | バックエンドのコンテナ実行環境 |
| GCP Cloud Storage | 画像・動画ファイルの保存 |
| Docker / Docker Compose | ローカル開発環境の構築 |

---

## セットアップ

### 必要なもの
- Docker / Docker Compose

### ローカル起動
```bash
cp .env.example .env.local
# .env.local を環境に合わせて編集
docker compose up
```

### 環境変数
| 変数名 | 説明 |
|---|---|
| `ENV` | `local` または `production` |
| `GCP_PROJECT_ID` | GCPプロジェクトID |
