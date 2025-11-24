# Streamlit UI - 医学論文管理システム

Obsidianと連携した論文管理のWebインターフェース

## 🚀 起動方法

### Windows

#### 方法1: ダブルクリック
`run_app.bat` をダブルクリック

#### 方法2: PowerShell
```powershell
.\run_app.ps1
```

#### 方法3: 直接実行
```powershell
streamlit run app\app.py
```

### Mac/Linux

#### 方法1: シェルスクリプト
```bash
./run_app.sh
```

#### 方法2: 直接実行
```bash
streamlit run app/app.py
```

---

## 📚 機能

### 1. ホーム画面 (app.py)
- システム概要
- 最近追加された論文
- Obsidianへのリンク

### 2. 📄 Add Paper
- PDFファイルアップロード
- メタデータ入力フォーム
- タグ選択（ドロップダウン）
- Obsidian自動連携

### 3. 📚 Browse
- 論文一覧表示
- フィルタ・検索
- 論文詳細表示
- Obsidianで開くボタン

### 4. 📊 Statistics
- 研究タイプ分布
- 年代別分布
- Perspectives分析
- タグ共起分析

---

## 🔗 Obsidian連携

### obsidian:// プロトコル

このアプリは `obsidian://` プロトコルを使用してObsidianと連携します。

**リンクの種類**:
- `obsidian://open?path=...` - 特定のノートを開く
- `obsidian://open?vault=...` - Vaultを開く

**使用例**:
```python
obsidian_uri = f"obsidian://open?path={note_path.absolute()}"
st.markdown(f'[Open in Obsidian]({obsidian_uri})')
```

### 連携の流れ

```
Streamlit UI
    ↓ 論文追加
catalog.json更新
    ↓
Obsidianノート生成
    ↓
Obsidianで閲覧（リンククリック）
```

---

## 🎨 カスタマイズ

### ポート番号変更

デフォルト: `8501`

変更する場合:
```bash
streamlit run app/app.py --server.port 8080
```

### テーマ変更

`.streamlit/config.toml` を作成:
```toml
[theme]
primaryColor = "#7c3aed"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

---

## 🐛 トラブルシューティング

### ポートが使用中

```bash
# 別のポートで起動
streamlit run app/app.py --server.port 8502
```

### Obsidianリンクが動かない

- Obsidianがインストールされているか確認
- `obsidian://` プロトコルが登録されているか確認
- パスが正しいか確認

### データが表示されない

- `data/catalog.json` が存在するか確認
- 論文が追加されているか確認

---

## 📁 ファイル構造

```
app/
├── app.py                       # メインアプリ
├── pages/
│   ├── 1_📄_Add_Paper.py       # 論文追加
│   ├── 2_📚_Browse.py          # 一覧
│   └── 3_📊_Statistics.py      # 統計
├── requirements_app.txt         # 依存ライブラリ
└── README.md                    # このファイル
```

---

## 🔧 開発者向け

### 新しいページを追加

1. `app/pages/` に `4_🔧_NewPage.py` を作成
2. Streamlitが自動的にサイドバーに追加

### データアクセス

```python
import json
from pathlib import Path

project_root = Path(__file__).parent.parent
catalog_path = project_root / "data" / "catalog.json"

with open(catalog_path, 'r', encoding='utf-8') as f:
    catalog = json.load(f)
```

---

## 📝 更新履歴

- v1.0 (2024-11-24): 初版リリース
  - 論文追加UI
  - 一覧・検索
  - 統計ダッシュボード
  - Obsidian連携

---

**Powered by**: Streamlit + Obsidian
