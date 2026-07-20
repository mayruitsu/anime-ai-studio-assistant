# SMPL→VRM リターゲティング 基礎学習メモ

## SMPLとは

人体の3D形状・姿勢を表す統計モデル。多くのモーション生成AI（MDMなど）はこのSMPL形式で結果を出力する。24個の関節（Pelvis、Hip、Knee、Shoulder、Elbow…）を持ち、各関節の「回転」で姿勢を表現する。

## 6D回転表現とは

3D回転は本来オイラー角（XYZ）や回転行列、クォータニオンなど複数の表し方があるが、AIモデルの出力としては**6D回転表現**（6つの数値の組）がよく使われる。理由は、オイラー角やクォータニオンには「不連続な値の飛び」が起きる箇所があり、ニューラルネットが学習しにくいため。6D表現はその問題を避けられる。

6D表現は「回転行列の1列目・2列目」の6つの数値で、そこから3列目を外積で復元して完全な回転行列に戻せる（MDMのユーティリティ関数`rotation_6d_to_matrix`が変換してくれる）。

```python
mat = rotation_6d_to_matrix(d6)          # 6D表現 → 3x3回転行列
euler = matrix_to_euler_angles(mat, "XYZ")  # 回転行列 → オイラー角（VRMのbone.rotationにそのまま渡せる形）
```

## SMPL関節 → VRM humanoidボーンの対応

SMPLとVRMは関節の名前も数も違うが、体の構造としては対応関係がある。使うのはSMPLの24関節のうち主要な17個だけで十分。

| SMPLインデックス | 意味 | VRMボーン名 |
|---|---|---|
| 0 | 骨盤 | hips |
| 3 | 脊椎下部 | spine |
| 6 | 脊椎中部 | chest |
| 12 | 首 | neck |
| 15 | 頭 | head |
| 16 / 17 | 左/右肩 | leftUpperArm / rightUpperArm |
| 18 / 19 | 左/右肘 | leftLowerArm / rightLowerArm |
| 20 / 21 | 左/右手首 | leftHand / rightHand |
| 1 / 2 | 左/右股関節 | leftUpperLeg / rightUpperLeg |
| 4 / 5 | 左/右膝 | leftLowerLeg / rightLowerLeg |
| 7 / 8 | 左/右足首 | leftFoot / rightFoot |

この対応表さえあれば、SMPLの回転パラメータをそのままVRMの各ボーンの`rotation`に設定でき、AIが生成したポーズをVRMモデルに反映できる。
