# Meta-Logic Tensor Language (MLTL) Specification

## Data Structure: Logical Quaternion
すべての情報ユニットは、以下の4成分で構成される。
$\Psi = \alpha + \beta\mathbf{G} + \gamma\mathbf{H} + \delta\mathbf{C}$

- **$\alpha$ (Truth Density)**: 真理密度 $[0, 1]$
- **$\mathbf{G}$ (Goal Orientation)**: 目標指向ベクトル
- **$\mathbf{H}$ (Historical Phase)**: 履歴位相ベクトル
- **$\mathbf{C}$ (Conflict Potential)**: 衝突ポテンシャル（摩擦係数）

## Operators
- **$\otimes$ (Conflict Operator)**: 二つの情報の不整合から「曲率」を抽出する。
- **$\oplus$ (Resolution Operator)**: 摩擦をエネルギーとして消費し、高次の均衡点へと情報を昇華させる。
