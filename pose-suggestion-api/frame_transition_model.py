"""「直近フレームの履歴＋テキスト」から「次の姿勢への相対回転（delta）」を予測する小規模モデル。

拡散モデル（`motion_diffusion_model.py`）と違い、1ステップ分の単純な回帰問題になったため、
Transformer・拡散過程は不要で、素直なMLPで十分と判断した。人間が生成結果を毎ステップ
手直しする前提の「たたき台」を作る用途なので、決定論的な出力（同じ入力なら常に同じ提案）
の方が扱いやすいという理由もある。

入力を現在の1フレームだけにすると、周期動作の位相・速度が分からず、`chain_frame_transitions.py`
で連鎖させたときに姿勢が崩壊することが分かった（PR #74・#75）。直近`history`フレーム分の
履歴を渡すことで、速度・位相を暗黙に読み取れるようにしている。

テキスト条件付けは`motion_diffusion_model.MotionDenoiser`と同様、CLIPではなく
自前語彙表・Embeddingをゼロから学習する（`motion_text_vocab.py`参照）。
"""
import torch
import torch.nn as nn


class FrameTransitionModel(nn.Module):
    def __init__(self, vocab_size: int, history: int = 3, pose_dim: int = 72,
                 model_dim: int = 128, hidden_dim: int = 256):
        super().__init__()
        self.history = history
        self.text_embed = nn.Embedding(vocab_size, model_dim)
        self.pose_in = nn.Linear(pose_dim * history, model_dim)
        self.mlp = nn.Sequential(
            nn.Linear(model_dim * 2, hidden_dim), nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim), nn.SiLU(),
            nn.Linear(hidden_dim, pose_dim),
        )

    def forward(self, history_poses: torch.Tensor, token_ids: torch.Tensor) -> torch.Tensor:
        """history_poses: (B, history, 24, 3)、token_ids: (B, L) -> 予測delta (B, 24, 3)。"""
        pose_flat = history_poses.reshape(history_poses.shape[0], -1)

        # token_ids==0（motion_text_vocab.PAD_TOKEN）を除外した平均プーリング
        mask = (token_ids != 0).unsqueeze(-1).float()
        text_cond = (self.text_embed(token_ids) * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)

        x = torch.cat([self.pose_in(pose_flat), text_cond], dim=-1)
        return self.mlp(x).reshape(-1, 24, 3)
