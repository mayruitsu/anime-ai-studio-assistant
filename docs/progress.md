# 開発進捗ログ

## 2026-05-03（続き2）

- MediaPipeを導入（`requirements.txt` に追加、Dockerfileにシステムライブラリを追加）
- 関節33点の検出動作確認スクリプト（`pose_test.py`）を作成
- MediaPipe基礎の学習メモを追加（Pose API・BGR/RGB変換・座標の読み方）
- フェーズ2（Python学習・バックエンド基礎）完了。次回よりフェーズ3（ポイント検出）を開始する

## 2026-05-03（続き）

- ポイントをドラッグで動かせる機能を実装（mousedown・mousemove・mouseup）
- フレーム追加・切り替え機能を実装（FramePanelコンポーネント、stateをAppに持ち上げ）
- フェーズ4（UIエディタ）完了。次回よりフェーズ2（Python・バックエンド基礎）を再開する

## 2026-05-03

- 画像アップロードUIを実装（ファイル選択 → URLを親コンポーネントに渡す）
- Canvas上にモック関節ポイントを表示（PoseCanvasコンポーネント、useRef・useEffect）

## 2026-04-20

- FastAPI最小構成を実装（`GET /health`、docker composeで動作確認）
- 差分チェックActionsをコード・ドキュメントで分けて表示するよう改善
- React環境構築（Vite + Docker、`http://localhost:5173` で動作確認）
- FastAPI基礎の学習メモを追加（import・クラス・インスタンス・デコレータ・HTTPメソッド）

## 2026-04-19

- README作成（開発ルール・プロジェクト概要）
- PRテンプレート・差分チェックActions追加
- CLAUDE.md作成（Claudeへの開発ルール定義）
- Docker環境構成追加（Dockerfile・docker-compose）
- docsディレクトリ構成追加（learn / pr-notes / tech）
- Docker技術解説追加（docs/tech/docker.md）
