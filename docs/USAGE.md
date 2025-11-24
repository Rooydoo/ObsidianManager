# 使用方法

医学論文管理システムの詳細な使い方

## 目次

1. [セットアップ](#セットアップ)
2. [論文追加の詳細](#論文追加の詳細)
3. [Obsidianでの閲覧](#obsidianでの閲覧)
4. [タグ管理](#タグ管理)
5. [エクスポート](#エクスポート)
6. [ベストプラクティス](#ベストプラクティス)

---

## セットアップ

### 初回セットアップ

1. **依存ライブラリのインストール**

```bash
pip install -r requirements.txt
```

2. **Obsidianのインストール**

https://obsidian.md/ から最新版をダウンロード

3. **Obsidian Vaultを開く**

- Obsidianを起動
- "Open folder as vault"
- `ObsidianManager/ObsidianVault`を選択

4. **Dataviewプラグインをインストール**

- Settings (⚙) → Community plugins
- "Turn on community plugins"を有効化
- Browse → 検索: "Dataview"
- Install → Enable

5. **設定ファイルの確認**

`config/config.yaml`を確認し、必要に応じて編集

---

## 論文追加の詳細

### 方法1: 対話的入力

最もシンプルな方法。コマンドラインで質問に答えていく形式。

```bash
python scripts/add_paper.py --pdf path/to/paper.pdf
```

**入力項目**:
- 基本情報（タイトル、著者、年、ジャーナルなど）
- 研究デザイン（study_type, sample_size, study_populationなど）
- 分類（perspectives: disease, method, analysis, population）
- キーワード
- アブストラクト（複数行、空行で終了）
- 要約（複数行、空行で終了）

**Tips**:
- 著者はカンマ区切り: `Yamada T, Suzuki K, Tanaka M`
- キーワードもカンマ区切り
- アブストラクトは複数行入力可能（最後に空行）

### 方法2: YAMLファイルから

事前にメタデータを準備する方法。複数論文の一括処理に便利。

```bash
# 1. テンプレートをコピー
cp templates/metadata_template.yaml my_paper.yaml

# 2. エディタで編集
vim my_paper.yaml

# 3. 論文追加
python scripts/add_paper.py \
  --pdf paper.pdf \
  --metadata my_paper.yaml
```

**YAMLファイル例**:

```yaml
title: "脳卒中患者の歩行解析"
authors:
  - Yamada T
  - Suzuki K
year: 2024
journal: "Journal of Biomechanics"
volume: "45"
issue: "3"
pages: "123-135"
doi: "10.1234/jbiomech.2024.001"
pmid: "12345678"

study_type: "cross_sectional"
study_design: "横断研究"
sample_size: 50
study_population: "脳卒中患者（発症後6ヶ月以上）"

perspectives:
  study_type: "cross_sectional"
  disease: "stroke"
  method: "gait_analysis"
  analysis: "machine_learning"
  population: "elderly"

keywords:
  - stroke
  - gait analysis
  - machine learning

language: "en"
read_status: "unread"
priority: "high"

abstract: |
  Background: Gait analysis is essential...
  Methods: We recruited 50 stroke patients...
  Results: Walking speed, stride length...
  Conclusions: Machine learning-based...

summary: |
  目的: 脳卒中患者の歩行パターンを解析...
  方法: 50名の患者を対象に...
  結果: 歩行速度が主要な予測因子...
  結論: 機械学習が有用...
```

### 方法3: Claude Webで要約生成（推奨）

**手順**:

1. PDFから情報を取得
2. Claude Webで`scripts/prompts/metadata_generation_prompt.txt`のプロンプトを使用
3. 出力されたYAMLを保存
4. `add_paper.py`で追加

**Claude Webでの使い方**:

```
[プロンプトをコピペ]

**論文タイトル**: 脳卒中患者の歩行パターン解析における機械学習の応用

**著者**: Yamada T, Suzuki K, Tanaka M

**掲載情報**: Journal of Biomechanics, 2024, 45(3):123-135

**DOI/PMID**: 10.1234/jbiomech.2024.001 / 12345678

**アブストラクト**:
```
Background: Gait analysis is essential for assessing...
[アブストラクト全文をペースト]
```
```

Claudeが構造化されたメタデータを生成します。

---

## Obsidianでの閲覧

### メインエントリポイント: Index.md

1. `Index.md`を開く
2. 統計情報を確認
3. 視点（Perspective）を選択

### 視点別の閲覧

#### Study Type Perspective

研究デザインから探す:
- RCT
- Systematic Review
- Observational Study
- Case Report
など

#### Disease Perspective

疾患から探す:
- Stroke
- Parkinson's Disease
- Fracture
など

#### Method Perspective

方法論から探す:
- Gait Analysis
- Motion Capture
- EMG
など

#### Analysis Perspective

解析手法から探す:
- Machine Learning
- Statistical Analysis
など

### Dataviewクエリのカスタマイズ

#### 例1: 特定条件で絞り込み

```dataview
TABLE title, authors, year, sample_size
FROM "Papers"
WHERE perspectives.disease = "stroke"
  AND perspectives.method = "gait_analysis"
  AND year >= 2020
SORT year DESC
```

#### 例2: 未読の高優先度論文

```dataview
TABLE title, perspectives.study_type, date_added
FROM "Papers"
WHERE read_status = "unread"
  AND priority = "high"
SORT date_added DESC
```

#### 例3: 年代別集計

```dataview
TABLE rows.file.link as "Papers", length(rows) as "Count"
FROM "Papers"
GROUP BY year
SORT year DESC
```

---

## タグ管理

### タグ一覧の確認

```bash
# 全メタタグのタグ一覧
python scripts/tag_manager.py list

# 特定のメタタグのみ
python scripts/tag_manager.py list --meta-tag disease
```

### 新しいタグの追加

```bash
python scripts/tag_manager.py add disease alzheimer \
  --aliases "AD" "alzheimer's_disease" "Alzheimer's"
```

### グループの管理

#### グループ一覧

```bash
python scripts/tag_manager.py list-groups
```

#### 新しいグループを作成

```bash
python scripts/tag_manager.py create-group \
  cognitive_disorders \
  disease \
  "認知機能障害" \
  --tags dementia alzheimer mild_cognitive_impairment \
  --description "認知機能に関連する疾患"
```

### 統計情報

```bash
python scripts/tag_manager.py stats
```

出力例:
```
総論文数: 150

[STUDY_TYPE 分布]
  rct: 25
  systematic_review: 18
  observational_study: 45
  ...

[DISEASE 分布]
  stroke: 35
  parkinson: 20
  fracture: 15
  ...
```

### グループ提案（共起分析）

```bash
python scripts/tag_manager.py suggest-groups --min-cooccurrence 3
```

共起回数が多いタグの組み合わせを提案します。

---

## エクスポート

### 基本的な使い方

1. **選択ノートを作成**

Obsidianで`selection.md`を作成:

```markdown
# My Research Project - Paper Selection

## Selected Papers

- [x] [[paper001]]
- [x] [[paper003]]
- [x] [[paper007]]
- [ ] [[paper010]]  # チェックなし = 除外
- [x] [[paper015]]
```

2. **エクスポート実行**

```bash
python scripts/export_selected.py \
  ObsidianVault/selection.md \
  exports/my_research_2024/
```

### エクスポートオプション

```bash
# 全文テキスト抽出をスキップ
python scripts/export_selected.py \
  selection.md \
  exports/output/ \
  --no-text

# RAGインデックス作成をスキップ
python scripts/export_selected.py \
  selection.md \
  exports/output/ \
  --no-rag

# 両方スキップ
python scripts/export_selected.py \
  selection.md \
  exports/output/ \
  --no-text --no-rag
```

### エクスポート結果の活用

#### RAGシステムとの統合

`rag_index.json`と`rag_config.json`を使用してRAGシステムに統合できます。

```python
import json

# RAGインデックス読み込み
with open('exports/my_project/rag_index.json', 'r') as f:
    rag_index = json.load(f)

# ドキュメント一覧
for doc in rag_index['documents']:
    print(doc['title'])
    print(doc['abstract'])
    # LangChain/LlamaIndexなどに渡す
```

#### メタデータ分析

```python
import json
from pathlib import Path

metadata_dir = Path('exports/my_project/metadata')

for metadata_file in metadata_dir.glob('*.json'):
    with open(metadata_file, 'r') as f:
        paper = json.load(f)
        # 分析処理
```

---

## ベストプラクティス

### 1. 論文追加時

- **要約は必ず作成**: 後で検索しやすくなります
- **タグは適切に選択**: 複数該当する場合は最も主要なものを
- **PDFファイル名**: わかりやすい名前にしておく（システムが自動でリネーム）

### 2. タグ管理

- **新しいタグは慎重に**: 既存タグで表現できないか確認
- **エイリアスを活用**: 表記ゆれを統一
- **グループを作成**: 関連タグをまとめて管理

### 3. Obsidian活用

- **定期的にIndex.mdを確認**: 全体像を把握
- **MOCノートを活用**: 視点別に論文を俯瞰
- **Dataviewクエリをカスタマイズ**: 自分の研究に合わせて調整

### 4. エクスポート

- **選択ノートを複数作成**: プロジェクトごとに管理
- **定期的にエクスポート**: バックアップにもなります
- **RAGシステムと統合**: 論文検索を高度化

### 5. Git管理

- **定期的にコミット**: 変更履歴を残す
- **プッシュは手動推奨**: `auto_push: false`に設定
- **PDFはGit LFS使用**: 大容量ファイルの管理

---

## よくある質問（FAQ）

### Q: PDFなしで論文を追加できますか？

A: はい、可能です。`--pdf`オプションなしで実行してください。

```bash
python scripts/add_paper.py
```

### Q: 後からPDFを追加できますか？

A: 手動で`papers/all_papers/{paper_id}.pdf`に配置し、
`catalog.json`の`pdf_path`を更新してください。

### Q: タグを変更したい場合は？

A: Obsidianノートのfrontmatterを編集し、
`catalog.json`も手動で更新してください。

### Q: 論文を削除したい場合は？

A: 以下を削除してください:
1. `papers/all_papers/{paper_id}.pdf`
2. `ObsidianVault/Papers/{paper_id}.md`
3. `catalog.json`から該当エントリ

---

## 次のステップ

- [README.md](../README.md) - システム概要
- [仕様書](../docs/SPECIFICATION.md) - 詳細仕様（元の仕様書を参照）
- [API Documentation](../docs/API.md) - スクリプトAPI（今後作成）

---

**Last Updated**: 2024-11-24
