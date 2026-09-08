# avatar-api：写真からVRMを生成するサービス

## 概要

写真（正面・背面・側面、side_is_rightで左右を指定）をアップロードすると、シルエット抽出→SMPLフィッティング→VRMエクスポートまでを行い、VRMファイルを返すサービス。`self-model-experiment`リポジトリで実装・検証済みのパイプラインを、`motion-api`と同じ構成（FastAPI、同期エンドポイント）でラップしている。

## motion-apiとの違い：Docker化していない理由

`motion-api`はDockerfileでGPU環境（PyTorch、CUDAランタイム）をコンテナ化しているが、`avatar-api`が依存する`nvdiffrast`は**CUDAコンパイラ（実行時にCUDAカーネルをJITビルドする）が必要**で、`motion-api`が使うCUDAランタイムだけのイメージでは動かない。WSL2上での環境構築時（`self-model-experiment/docs/tech/nvdiffrast-wsl2-setup.md`）も、gccのバージョン調整やglibcヘッダーの衝突回避など、Docker化には持ち越しの検証が必要な問題に複数遭遇していた。

そのため現時点では**Docker化を見送り、WSL2の既存GPU環境で直接`uvicorn`を起動する**運用とした。Docker化はDockerfile側でCUDA開発環境（`nvidia/cuda:*-devel`系イメージ等）を使うことで対応できる見込みだが、別途の検証が必要な今後の課題とする。

## 起動方法（現時点、WSL2）

```bash
cd avatar-api
source /root/self-model-experiment/.venv/bin/activate  # nvdiffrast等が入ったvenv
export AVATAR_API_SMPL_MODEL_PATH=/path/to/basicmodel_neutral_lbs_10_207_0_v1.1.0.pkl
uvicorn app:app --host 0.0.0.0 --port 8091
```

## 動作確認

`curl`で直接HTTPリクエストを送り、AI生成画像（正面・背面・側面）から実際にVRMファイルが生成されることを確認した（HTTP 200、約500KBの`.vrm`ファイル）。さらにPlaywright＋実際のフロントエンド（three-vrm）で、生成されたVRMファイルの読み込み・表示を確認した。

**「写真アップロード→API→VRM生成→studioでの表示」が、フロントエンドUIを介さない直接API呼び出しレベルでは動作することを確認済み。** フロントエンドからの実行UI自体は別タスクとして進行中。

## 今後の課題

- Docker化（CUDA開発環境イメージでの構築検証）
- `docker-compose.yml`への統合
- リクエストのバリデーション・エラーハンドリング（現状は最小限）
