"""VRMのXYZオイラー角（ラジアン、three.jsの既定順）とSMPLの軸角度を相互変換するヘルパー。

self-model-experimentの`cmu_to_smpl.py`（度単位、ASF/AMC向け）と同じ数学
（R = Rx @ Ry @ Rz、軸角度への変換はロドリゲスの公式の逆変換）をラジアン単位に移植したもの。
"""
import numpy as np


def euler_xyz_to_matrix(angles_rad) -> np.ndarray:
    x, y, z = angles_rad
    rx = np.array([[1, 0, 0], [0, np.cos(x), -np.sin(x)], [0, np.sin(x), np.cos(x)]])
    ry = np.array([[np.cos(y), 0, np.sin(y)], [0, 1, 0], [-np.sin(y), 0, np.cos(y)]])
    rz = np.array([[np.cos(z), -np.sin(z), 0], [np.sin(z), np.cos(z), 0], [0, 0, 1]])
    return rx @ ry @ rz


def matrix_to_euler_xyz(rot: np.ndarray):
    y = np.arcsin(np.clip(rot[0, 2], -1.0, 1.0))
    x = np.arctan2(-rot[1, 2], rot[2, 2])
    z = np.arctan2(-rot[0, 1], rot[0, 0])
    return x, y, z


def matrix_to_axis_angle(rot: np.ndarray) -> np.ndarray:
    angle = np.arccos(np.clip((np.trace(rot) - 1) / 2, -1.0, 1.0))
    if angle < 1e-8:
        return np.zeros(3)
    axis = np.array([rot[2, 1] - rot[1, 2], rot[0, 2] - rot[2, 0], rot[1, 0] - rot[0, 1]]) / (2 * np.sin(angle))
    return axis * angle
