# Claude向け開発ルール

## プロジェクト概要

1枚の人型画像から関節ポイントをAIで自動検出し、ユーザーがフレームごとに操作してアニメーションを作成するアシスタントツール。画像生成・自動アニメーション生成は行わない。

## 技術スタック

- ポイント検出AI: MediaPipe Pose
- バックエンド: Python + FastAPI
- フロントエンド: React + Canvas API
- 動画出力: OpenCV
- インフラ: GCP（Cloud Run + Cloud Storage）
- 開発環境: Docker（docker-compose）

## 環境構成

- ローカル：docker-compose + `.env.local` で環境変数を管理
- デプロイ：Cloud Run の環境変数で設定
- `.env.local` はgitignore対象。`.env.example` をもとに作成する

## コーディングルール

- 作業前に必ずブランチを作成する（mainへの直接pushは禁止）
- ブランチ名には連番を付ける（例：`feature/01-topic`、`learn/01-topic`）
- 1PRの差分は削除を含めて100行以内に収める
- PRタイトルは必ず日本語で記載する

## コミットメッセージ

- 日本語で簡潔に記載する
- 例：`MediaPipeで関節ポイント検出を実装`

## ドキュメントルール

| ディレクトリ | 用途 | 管理 |
|---|---|---|
| `docs/learn/` | 学習メモ | 手動 |
| `docs/pr-notes/` | PRごとのコード解説 | GitHub Actions自動生成 |
| `docs/tech/` | 技術・ツールの解説（Docker、GCPなど） | 手動 |
| `docs/progress.md` | 日付ごとの開発進捗ログ | 手動 |
| `docs/roadmap.md` | 機能一覧とステータス管理 | 手動 |

- 新しい技術・ツールを導入したら `docs/tech/` に解説を追加する
- 解説はPRに含めてよい（差分100行のカウント対象）
- タスクが完了したら `docs/roadmap.md` のステータスを更新する
- 作業日に `docs/progress.md` へ実施内容を追記する

## コード完成時の対応

Pythonコードが完成したら、以下の内容を解説する：
- 使用したライブラリとその役割
- コードの処理の流れ
- 重要な関数・クラスの説明
- 学習ポイント（初学者向けに補足）
