# GyroOS

**Gyro Process、Operator Response、Context-aware Runtime、Dynamic Equivalence のための実行アーキテクチャ**

---

## 📄 公開情報

GyroOS v4.0 の英語版プレプリントが Jxiv で公開されました。

- Jxiv English: https://doi.org/10.51094/jxiv.5842
- Zenodo archive: https://doi.org/10.5281/zenodo.21641266
- GitHub Release: v4.0.0

日本語翻訳版は、公開済み英語版との整合を確認したうえで準備・投稿します。

---

## 🧭 GyroOSとは何か

GyroOS は **Gyro Logic** の実装層である。

GyroOS は Gyro Logic を再定義しない。  
Gyro Logic を実行可能なランタイムシステムとして実装する。

不変の理論コアは次である。

```text
Structure → Slice → Stability
```

GyroOS は、このコアを Runtime Continuity へ写像する。Slice の内部的なRuntime読解は次である。

```text
Structure
→ Slice {
    Operator Orientation
    → slice-ing
    → slice-done
  }
→ Stability
→ Operator Response
→ Next Process
```

Operator Orientation、slice-ing、slice-done は Slice 内部の区別であり、追加のCore Stageではない。

GyroOS は応用層ではない。  
GyroAuth は GyroOS の上に構築される応用層である。

---

## 🧩 スタック上の位置づけ

```text
Gyro Logic   = 理論層
GyroOS       = 実装層
GyroAuth     = 応用層
```

原則：

```text
Gyro Logic は GyroOS に依存しない。
GyroOS は Gyro Logic を実装する。
GyroAuth は GyroOS を応用する。
```

GyroOS は、実装都合によって Gyro Logic の定義を変更してはならない。

### システム構成とフロー

![GyroOS システム構成図・フロー図](figures/gyroos_system_architecture_flow_jp.svg)

この図は、Gyro Logicの不変CoreからGyroOS Runtime、vNext read-only projection、POSTのみのInspection API、明示的参照によるF〜W hierarchy、外部のGyroAuth consumer boundaryまでを一枚で示す。

公開用マスター図版：

- 日本語SVG：`figures/gyroos_system_architecture_flow_jp.svg`
- 英語SVG：`figures/gyroos_system_architecture_flow_en.svg`
- 構成図の説明・キャプション案：`docs/292_gyroos_system_architecture_flow_overview.md`

---

## 🔁 コア原則

コア原則は常に次である。

```text
Structure → Slice → Stability
```

これは時間なしの Gyro Unit である。

GyroOS は、この構造を Gyro Process としてRuntime上で読む。

```text
Structure
→ Slice {
    Operator Orientation
    → slice-ing
    → slice-done
  }
→ Stability
→ Operator Response
```

Gyro Loop は Structure → Slice → Stability を置き換えるものではない。

Gyro Loop は、Operator Response によって Gyro Process が反復される構造である。
