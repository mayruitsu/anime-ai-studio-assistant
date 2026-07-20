from rotation import calc_rotation_angles

base_points = [{"x": 0.5, "y": 0.5} for _ in range(33)]
target_points = [{"x": 0.5, "y": 0.5} for _ in range(33)]

# 左上腕（肩11→肘13）を「水平右向き」から「真下向き」に90度動かす例
base_points[11] = {"x": 0.4, "y": 0.3}
base_points[13] = {"x": 0.6, "y": 0.3}
target_points[11] = {"x": 0.4, "y": 0.3}
target_points[13] = {"x": 0.4, "y": 0.5}

angles = calc_rotation_angles(base_points, target_points)
print(f"upper_arm_left の回転角: {angles['upper_arm_left']:.1f}度（期待値: 90.0度）")
