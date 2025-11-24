# タググループ一覧

タググループは、関連するタグをまとめたものです。

## グループの役割

- 関連する論文を横断的に検索
- タグの共起パターンの可視化
- 研究領域の俯瞰

## 主要グループ

### Study Type Groups
- **Clinical Trials** (`clinical_trials`) - 介入研究
- **Review Articles** (`review_articles`) - レビュー論文
- **Observational Studies** (`observational_studies`) - 観察研究
- **Case Studies** (`case_studies`) - 症例研究

### Disease Groups
- **Neurological Disorders** (`neurological_disorders`) - 神経疾患
- **Musculoskeletal Disorders** (`musculoskeletal_disorders`) - 筋骨格系疾患

### Method Groups
- **Kinematic Methods** (`kinematic_methods`) - 運動学的手法
- **Kinetic Methods** (`kinetic_methods`) - 動力学的手法
- **Imaging Methods** (`imaging_methods`) - 画像診断

### Analysis Groups
- **AI Analysis** (`ai_analysis`) - AI・機械学習
- **Statistical Methods** (`statistical_methods`) - 統計解析
- **Signal Processing** (`signal_processing`) - 信号処理

## グループ管理

新しいグループは `scripts/tag_manager.py` を使用して作成できます。

```bash
python scripts/tag_manager.py create-group \
  group_name meta_tag display_name \
  --tags tag1 tag2 tag3 \
  --description "説明"
```

---

[← Back to Index](../Index.md)
