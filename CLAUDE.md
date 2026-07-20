# Claude向け開発ルール

## プロジェクト概要

3Dアバター（VRM形式）をポインター操作でポージングし、アニメ的な動き・レンダリングでアニメーションを作成するアシスタントツール。画像生成AIは使わない（3Dモデルの操作・レンダリングのみ）。

方針転換の経緯は [docs/design/3d-vrm-pivot.md](design/3d-vrm-pivot.md) 参照。旧方針（1枚の実写真/イラストから関節検出し、2D剛体パーツを切り抜いて動かす方式）はフェーズ6・7として実装済みだが、ダイナミックな動きに対応できない構造的な限界が判明し、一旦保留とした。

並行して、ユーザー自身の写真から3Dモデルを生成する研究（トラックB）にも取り組む。

## 技術スタック

- 3Dモデル: VRM形式（VRoid Studio等で作成されたアニメ調アバター）
- 3D描画: Three.js + `@pixiv/three-vrm`
- ポイント検出AI（旧方式・保留中）: MediaPipe Pose
- バックエンド: Python + FastAPI
- フロントエンド: React + Three.js（旧方式ではCanvas API）
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
- 1PRのコード差分は削除を含めて100行以内に収める（ドキュメントは行数制限なし）
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
- 解説はPRに含めてよい（100行制限のカウント対象外）
- タスクが完了したら `docs/roadmap.md` のステータスを更新する
- 作業日に `docs/progress.md` へ実施内容を追記する

## コード完成時の対応

Pythonコードが完成したら、以下の内容を解説する：
- 使用したライブラリとその役割
- コードの処理の流れ
- 重要な関数・クラスの説明
- 学習ポイント（初学者向けに補足）
