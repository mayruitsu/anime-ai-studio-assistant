# motion-api（MDMによるモーション自動生成）セットアップ

`motion-api`サービスは、テキストから動き（関節角度シーケンス）を生成するAIモデル「MDM（Motion Diffusion Model）」を呼び出し、VRMの骨格に合わせて変換して返すAPIです。GPU（NVIDIA、CUDA対応）が前提です。

## 事前準備：MDM本体を別ディレクトリに用意する

MDM（[GuyTevet/motion-diffusion-model](https://github.com/GuyTevet/motion-diffusion-model)）は大きな第三者リポジトリ・学習済みモデルのため、このプロジェクトには含めていません。以下を**このリポジトリの外**に用意してください。

1. リポジトリをクローン
   ```
   git clone https://github.com/GuyTevet/motion-diffusion-model.git
   ```
2. SMPLモデルファイルを取得（`prepare/download_smpl_files.sh`。gitのautocrlfでバイナリが壊れる場合は`core.autocrlf=false`にするか、該当ファイルをGitHubから直接ダウンロードし直す）
3. HumanML3Dのテキストデータを取得し`dataset/HumanML3D`に配置（[EricGuo5513/HumanML3D](https://github.com/EricGuo5513/HumanML3D)の`texts.zip`を展開）
4. 学習済みチェックポイント（`humanml-encoder-512-50steps`など）をダウンロードし`save/`に展開

## .envの設定

プロジェクトルートに`.env`（`.env.local`とは別、docker composeの変数展開用）を作成し、MDMを配置したパスを指定します。

```
MDM_REPO_PATH=/path/to/motion-diffusion-model
```

`.env`は`.gitignore`対象です。

## 起動

```
docker compose up motion-api
```

`http://localhost:8090/generate-motion` に `{"text": "..."}` をPOSTすると、VRMボーン名でのポーズ列（JSON）が返ります。

## 既知の制約

- 1回の生成に**2〜3分程度**かかります（SMPLify=joints2smplによる、xyz座標→SMPL回転パラメータへのフィッティング処理がボトルネック）
- モデル・データセットはリクエストのたびに読み込み直す簡易実装です（高速化する場合は常駐プロセス化を検討）
