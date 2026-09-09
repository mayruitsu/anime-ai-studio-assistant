# 引き継ぎ資料：全体状況とルール（2026-09-09時点）

作成日: 2026-09-08（初版）／2026-09-09大幅更新

このファイルは「プロジェクト全体の状況とルール」をまとめたもの。**次に着手する具体的タスク**（自前モーション生成モデルの開発）は`motion-generation-from-scratch-handoff.md`（同じフォルダ）を参照。

## 1. これまでの経緯（要約）

「4方向イラストから3Dアバターを作り、会話しながらポーズ・アニメーションをつけて動画にする」を目標に、`self-model-experiment`（3Dアバター生成の研究）と`anime-ai-studio-assistant`（ポージング・アニメーション作成アプリ）の2リポジトリで開発を進めている。

- SMPL（人体統計モデル、写真非学習）をテンプレートにした3D復元パイプラインへの方針転換
- 会話インターフェース：OLMo（ファインチューニング、汎用対話）＋自作の限定モデル（意味解析、ツール呼び出し先）の2階層構成
- 全体を6トラック（A〜F）に分解した実装計画（`docs/design/animation-creation-implementation-plan.md`、両リポジトリに同期済み）
- 両リポジトリのCLAUDE.mdに自律実装モードを追記済み（4節参照）

## 2. 進捗状況（トラック別、2026-09-09時点）

| トラック | 状態 | 備考 |
|---|---|---|
| A：SMPLパイプライン本体 | 🔄 大部分完了 | SMPL読み込み〜シルエットフィッティング〜**VRMエクスポート**まで完了。実写真相当の入力（AI生成画像）でエンドツーエンド動作確認済み。陰影による詳細化（Stage C）は未着手（過去の検証で物理的に不安定と判明、優先度低） |
| B：ツールAPI化＋橋渡し（`anime-ai-studio-assistant`） | ✅ 完了 | |
| C：限定的な自作モデル（骨格編集の意味解析） | ✅ 完了 | 完全一致率95.7% |
| D：会話アシスタントサービス（OLMo） | ✅ 主要ステップ完了 | サービス土台・ツール呼び出し基盤・ファインチューニング用データ生成・LoRAファインチューニング実行評価まで完了。**ツール呼び出し精度：ファインチューニング前10.6%→後100.0%**。Docker化・docker-compose統合も完了。残るのは本物のapiサービスとの実機統合のみ（mediapipeバージョン非互換で現環境では未検証） |
| E：統合・エンドツーエンドテスト | ⬜ 未着手 | |
| F：写真からのアバター生成UI統合（新設） | ✅ 完了 | `avatar-api`サービス化（self-model-experimentのパイプラインをmotion-apiと同じ構成でラップ）。フロントエンドに写真アップロードUIを追加し、Playwrightで「写真3枚→生成ボタン→アバター表示」が実際に動作することを確認 |

詳細・PR番号は両リポジトリの`docs/design/animation-creation-implementation-plan.md`、`docs/progress.md`参照。

## 3. 現在のPR状況

両リポジトリともスタック方式（各PRが前のPRのブランチから派生）で大量のPRが未マージのまま蓄積している。

- `self-model-experiment`：PR #14〜#48程度
- `anime-ai-studio-assistant`：PR #38〜#78程度

マージするかどうか・タイミングはユーザーの判断待ち（自律実装モードでもマージだけは必ず確認する運用）。

## 4. 自律実装モードの設定状況

両リポジトリのCLAUDE.mdに以下を追記済み。

```markdown
## 自律実装モードについて（2026-09-08〜）

`docs/design/animation-creation-implementation-plan.md`に従った実装作業について、
Claudeは以下の操作をユーザーへの確認なしに行ってよい：
- ブランチの作成
- ファイルの追加・編集
- コミット・push（mainへの直接pushは元々禁止のため対象外）
- PRの作成

以下は必ずユーザーに確認する：
- PRのマージ
- 外部サービスへの登録・アカウント作成
- 費用が発生する操作（クラウドGPU利用等）
- 計画外の大きな設計変更
```

さらにユーザーから口頭で「基本的にそういうのも自己判断で進めていい。どうしても判断が付かない場合はユーザーの確認を待ち、その間は別タスクを進める」という運用方針の追加確認あり（2026-09-09）。

## 5. 環境情報

- **WSL2（Ubuntu）**：`/root/self-model-experiment`にGPU環境一式（PyTorch 2.11.0+cu128、nvdiffrast、transformers、peft、accelerate等インストール済み）。GPU：RTX 5070（VRAM約12.8GB）
- **Windows側venv**：`/tmp/smpl_ml_venv`相当（CPU版torch、transformers、fastapi等）。GPU不要な検証・OLMoのCPU推論確認等はこちらで実施
- HuggingFaceモデルキャッシュはWindows側（`C:\Users\8amat\.cache\huggingface`）にあり、WSL2から`HF_HOME=/mnt/c/Users/8amat/.cache/huggingface`を指定することで共有・再利用できる

## 6. 権限設定を変えても人の確認が必要な地点（ガードレール、実績ベース）

- **Git認証情報の取得・設定**（`gh auth token`等）、**プロセスの強制終了**（`kill`/`pkill`）：Claude Codeの安全機構でブロックされる
- **`git reset --hard`等の破壊的コマンド**：同上でブロックされる場合がある（`git restore --source=HEAD --staged --worktree .`は同等の復旧に使える代替）
- **PRのマージ判断・外部登録・費用発生操作**：都度確認

## 7. 実装中に随時参照するドキュメント

- 両リポジトリの`docs/design/animation-creation-implementation-plan.md`（実装順序・進捗・マイルストーン）
- `self-model-experiment/docs/tech/`配下（silhouette-fitting-experiment.md、vrm-export.md等）
- `anime-ai-studio-assistant/docs/tech/`配下（avatar-api.md、chat-api.md等）
- **次のタスクの詳細**：`motion-generation-from-scratch-handoff.md`（本フォルダ内）
