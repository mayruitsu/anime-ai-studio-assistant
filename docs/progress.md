# 開発進捗ログ

## 2026-07-20

- `video.py` を新規作成 — OpenCV で全フレームの関節ポイントを元画像に描画し MP4 動画を生成
- `POST /export-video` エンドポイントを追加 — 画像とフレームデータを受け取り動画を返す
- フロントに「動画を書き出す」ボタンを追加 — クリックで `animation.mp4` をダウンロード
- CLAUDE.md のルールを修正 — ドキュメントを100行制限のカウント対象外に変更
- フェーズ5（動画出力）完了。次回よりフェーズ6（GCPデプロイ）の実装方針を検討する

## 2026-05-17

- フロントエンドから `POST /detect-pose` を呼び出し、実際の関節33点を Canvas に表示
- モックポイントを削除し、API検出結果に置き換え
- FastAPI に CORS ミドルウェアを追加（フロント:5173 ↔ API:8080 の通信を許可）
- 次回よりフェーズ5（動画出力）を進める

## 2026-05-13

- `POST /detect-pose` エンドポイントを実装（画像を受け取り関節33点をJSONで返す）
- 検出ロジックを `pose.py` に分離（main.py はルーティングに集中）
- `python-multipart` を追加（ファイルアップロードに必要）
- フェーズ3（ポイント検出）完了。次回よりフェーズ4との連携（フロントからAPIを呼ぶ）を進める

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
