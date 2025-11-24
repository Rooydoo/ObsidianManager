# 医学論文管理システム v1.0

PDFを物理的に1箇所に集約保存し、メタデータとObsidianで多次元的に管理する医学論文管理システム

## 特徴

- **シンプルな物理層**: PDFは`papers/all_papers/`に一元管理
- **柔軟な論理層**: メタデータで多次元分類、Obsidianで動的閲覧
- **階層的タグシステム**: メタタグ→グループ→個別タグの3階層構造
- **手動 ↔ AI自動化**: Phase 1は手動入力、Phase 2でClaude API対応
- **RAG対応**: エクスポート機能でRAGシステム連携

## クイックスタート

### 1. 環境構築

```bash
# 依存ライブラリのインストール
pip install -r requirements.txt

# Obsidianのインストール（公式サイトから）
# https://obsidian.md/
```

### 2. Obsidian Vaultの設定

1. Obsidianを起動
2. "Open folder as vault"を選択
3. `ObsidianVault`フォルダを選択
4. Community Plugins を有効化
   - Settings → Community plugins → Turn on community plugins
5. Dataviewプラグインをインストール
   - Browse → 検索: "Dataview" → Install → Enable

### 3. 論文の追加

#### 方法1: 対話的入力

```bash
python scripts/add_paper.py --pdf path/to/paper.pdf
```

対話形式でメタデータを入力します。

#### 方法2: YAMLファイルから

```bash
# テンプレートをコピー
cp templates/metadata_template.yaml my_paper_metadata.yaml

# エディタで編集
vim my_paper_metadata.yaml

# 論文を追加
python scripts/add_paper.py \
  --pdf path/to/paper.pdf \
  --metadata my_paper_metadata.yaml
```

### 4. Obsidianで閲覧

1. Obsidianで`Index.md`を開く
2. 視点（Perspective）を選択
   - Study Type（研究デザイン）
   - Disease（疾患）
   - Method（方法論）
   - Analysis（解析手法）
3. Dataviewクエリで論文を絞り込み
4. 論文ノートをクリックして詳細を確認

## ディレクトリ構造

```
ObsidianManager/
├── papers/all_papers/          # PDF保存先（Git管理外）
├── ObsidianVault/              # Obsidian Vault
│   ├── Index.md                # メインエントリポイント
│   ├── Papers/                 # 個別論文ノート
│   ├── MOC/                    # 視点別インデックス
│   └── Groups/                 # グループMOC
├── data/                       # メタデータDB
│   ├── catalog.json            # 統合カタログ
│   ├── tag_hierarchy.json      # タグ階層定義
│   └── tag_groups.json         # グループ定義
├── scripts/                    # Pythonスクリプト
│   ├── add_paper.py            # 論文追加
│   ├── tag_manager.py          # タグ管理
│   ├── export_selected.py      # エクスポート
│   └── utils/                  # ユーティリティ
├── templates/                  # テンプレート
├── config/                     # 設定ファイル
├── exports/                    # エクスポート先
└── README.md                   # このファイル
```

## 主要機能

### 論文追加

```bash
# 基本的な使い方
python scripts/add_paper.py --pdf paper.pdf

# メタデータYAMLから
python scripts/add_paper.py --pdf paper.pdf --metadata metadata.yaml
```

自動的に：
- PDFを`papers/all_papers/`にコピー
- アブストラクトを抽出（可能な場合）
- タグを正規化
- Obsidianノートを生成
- MOCノートを更新
- Gitコミット（設定による）

### タグ管理

```bash
# タグ一覧
python scripts/tag_manager.py list

# 特定のメタタグのみ
python scripts/tag_manager.py list --meta-tag disease

# 新しいタグを追加
python scripts/tag_manager.py add disease alzheimer \
  --aliases "AD" "alzheimer's_disease"

# グループ一覧
python scripts/tag_manager.py list-groups

# グループ作成
python scripts/tag_manager.py create-group \
  cognitive_disorders disease "認知機能障害" \
  --tags dementia alzheimer mild_cognitive_impairment \
  --description "認知機能に関連する疾患"

# 統計情報
python scripts/tag_manager.py stats

# グループ提案（共起分析）
python scripts/tag_manager.py suggest-groups --min-cooccurrence 3
```

### 論文エクスポート

1. Obsidianで選択ノートを作成（例: `selection.md`）

```markdown
# Export Selection

- [x] [[paper001]]
- [x] [[paper003]]
- [ ] [[paper005]]  # チェックなしは除外
```

2. エクスポート実行

```bash
python scripts/export_selected.py \
  ObsidianVault/selection.md \
  exports/my_project/
```

出力構造：
```
exports/my_project/
├── README.md              # マニフェスト
├── manifest.json          # メタデータ
├── rag_index.json         # RAG用インデックス
├── rag_config.json        # RAG設定
├── pdfs/                  # PDFファイル
├── texts/                 # 全文テキスト
└── metadata/              # 詳細メタデータJSON
```

## タグシステム

### 3階層構造

1. **メタタグ（Level 1）**: study_type, disease, method, analysis, population
2. **タググループ（Level 2）**: 関連タグのまとまり（例: neurological_disorders）
3. **個別タグ + エイリアス（Level 3）**: 正規タグと同義語（例: stroke, CVA）

### 主要メタタグ

- **study_type**（必須）: 研究デザイン
  - rct, systematic_review, meta_analysis, cohort_study, cross_sectional など
- **disease**: 疾患・病態
  - stroke, parkinson, fracture, osteoarthritis など
- **method**: 測定・評価方法
  - gait_analysis, motion_capture, emg, force_plate など
- **analysis**: 解析手法
  - machine_learning, statistical_analysis, time_series など
- **population**: 対象集団
  - elderly, pediatric, athletes, community_dwelling など

### タグ正規化

エイリアス（表記ゆれ）は自動的に正規タグに変換されます。

例:
- `CVA` → `stroke`
- `randomized_controlled_trial` → `rct`
- `gait_study` → `gait_analysis`

## Obsidian活用法

### Dataviewクエリ例

#### 特定の疾患 + 方法論で絞り込み

```dataview
TABLE title, authors, year
FROM "Papers"
WHERE perspectives.disease = "stroke"
  AND perspectives.method = "gait_analysis"
SORT year DESC
```

#### 最近の高優先度論文

```dataview
TABLE title, year, perspectives.study_type
FROM "Papers"
WHERE priority = "high"
  AND date_added >= date(today) - dur(30 days)
SORT date_added DESC
```

#### RCTのみ、2020年以降

```dataview
TABLE title, authors, sample_size
FROM "Papers"
WHERE perspectives.study_type = "rct"
  AND year >= 2020
SORT year DESC
```

### MOCノート

視点別のMOCノートは自動生成されます。
- `stroke_view.md` - 脳卒中関連論文
- `gait_analysis_view.md` - 歩行解析関連論文
- `machine_learning_view.md` - 機械学習関連論文

## 設定

### config/config.yaml

```yaml
# パス設定
paths:
  papers_dir: ./papers/all_papers
  obsidian_vault: ./ObsidianVault
  # ...

# Git設定
git:
  enabled: true
  auto_commit: true
  auto_push: false  # 推奨: false

# 処理モード
processing:
  default_mode: manual  # Phase 1

# エクスポート設定
export:
  extract_full_text: true
  create_rag_index: true
```

## Phase 2（将来実装）

### Claude API自動化

```bash
# 自動モード（Phase 2）
python scripts/add_paper.py --mode auto --pdf paper.pdf
```

自動実行:
- アブストラクト抽出
- Claude APIで要約生成
- カテゴリ・タグ自動推定
- Obsidianノート生成

### プロンプト管理

`scripts/prompts/metadata_generation_prompt.txt`を編集して、
Claude APIに送信するプロンプトをカスタマイズできます。

## トラブルシューティング

### Dataviewクエリが動かない

- Community Pluginsが有効化されているか確認
- Dataviewプラグインがインストール・有効化されているか確認
- クエリの構文を確認（MDXクエリブロックは ` ```dataview ` で囲む）

### PDFが見つからない

- `pdf_path`が絶対パスになっているか確認
- ファイルが実際に存在するか確認

### Gitプッシュエラー

- `config/config.yaml`で`auto_push: false`に設定することを推奨
- 手動で`git push`を実行

## ライセンス

MIT License

## 貢献

Issue・PRを歓迎します。

## 変更履歴

- v1.0 (2024-11-24): Phase 1 初版リリース
  - 手動モード実装
  - 階層的タグシステム
  - Obsidian統合
  - エクスポート機能

---

**Developed by**: Medical Paper Management System Team
**Documentation**: See `docs/` directory for detailed specifications
