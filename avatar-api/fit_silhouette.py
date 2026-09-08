"""4方向のシルエット画像から、SMPLの体型パラメータ(β)とルート向きを最適化する。

撮影プロトコル（docs/roadmap.md参照）では、体のポーズ自体は既知の固定ポーズ
（Tポーズ、または`poses.py`で定義した腕を下げたポーズ等）である前提のため、
ここでは体型(β)とカメラに対する体の向き（ルート関節の回転）のみを最適化対象とする。
それ以外の23関節は指定された固定ポーズのまま変化させない。
"""
import torch

from poses import arms_down_pose_torch, t_pose
from silhouette_renderer import look_at_orthographic, render_silhouette

VIEW_ANGLES = (0, 90, 180, 270)


def render_views(glctx, model, betas, root_orient, kintree_parents, center, resolution, distance, extent,
                  base_pose=None):
    from smpl_lbs import pose_and_skin

    pose = t_pose().to(betas.device) if base_pose is None else base_pose.to(betas.device)
    pose = torch.cat([root_orient.unsqueeze(0), pose[1:]], dim=0)
    v_shaped = model.shaped_template(betas)
    joints = model.joint_locations(v_shaped)
    vertices = pose_and_skin(v_shaped, joints, pose, model.posedirs, model.weights, kintree_parents)

    silhouettes = []
    for angle in VIEW_ANGLES:
        mvp = look_at_orthographic(angle, center, distance, extent)
        silhouettes.append(render_silhouette(glctx, vertices, model.faces, mvp, resolution))
    return silhouettes


def fit_betas_and_root(glctx, model, targets, kintree_parents, center, resolution, distance, extent,
                        num_steps=200, lr=0.05, num_betas=10, log_every=0, beta_reg_weight=0.04,
                        base_pose=None, init_shoulder_deg=None):
    """targets（4方向のシルエット、各(resolution,resolution)の0/1テンソル）にβ・ルート向きを最適化で合わせる。

    beta_reg_weight：βに対する正則化（SMPLのβは平均0・分散1の統計的な主成分のため、
    0から極端に離れた値にならないようペナルティをかける。SMPLifyのshape priorと同じ考え方）。
    これが無いと、シルエットの一部分だけを説明しようとしてβが発散することがある。

    init_shoulder_deg：Noneでなければ、腕を下げた角度（左右対称の1自由度）も
    この初期値から最適化対象にする（撮影写真から目視で角度を計測する誤差を減らすため）。
    その場合`base_pose`は無視される。
    """
    device = targets[0].device
    betas = torch.zeros(num_betas, device=device, requires_grad=True)
    root_orient = torch.zeros(3, device=device, requires_grad=True)
    params = [betas, root_orient]

    shoulder_angle = None
    if init_shoulder_deg is not None:
        shoulder_angle = torch.deg2rad(torch.tensor(float(init_shoulder_deg), device=device)).requires_grad_(True)
        params.append(shoulder_angle)
    optimizer = torch.optim.Adam(params, lr=lr)

    loss_history = []
    for step in range(num_steps):
        pose = arms_down_pose_torch(shoulder_angle) if shoulder_angle is not None else base_pose
        silhouettes = render_views(glctx, model, betas, root_orient, kintree_parents, center, resolution, distance,
                                    extent, base_pose=pose)
        per_view_loss = [((s - t) ** 2).mean() for s, t in zip(silhouettes, targets)]
        loss = sum(per_view_loss) + beta_reg_weight * (betas ** 2).sum()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        loss_history.append(loss.item())
        if log_every and step % log_every == 0:
            views = [f"{v.item():.4f}" for v in per_view_loss]
            shoulder_info = f" shoulder_deg={torch.rad2deg(shoulder_angle).item():.1f}" if shoulder_angle is not None else ""
            print(f"  step {step}: loss={loss.item():.4f} per_view={views} beta_norm={betas.norm().item():.3f}{shoulder_info}")

    shoulder_deg_result = torch.rad2deg(shoulder_angle).item() if shoulder_angle is not None else None
    return betas.detach(), root_orient.detach(), loss_history, shoulder_deg_result
