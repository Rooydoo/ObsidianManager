# Windows セットアップガイド

Windowsでの医学論文管理システムのセットアップ方法

---

## 前提条件

- Windows 10/11
- Python 3.9以上
- Git for Windows
- Obsidian

---

## 1. Python環境のセットアップ

### Python インストール

1. https://www.python.org/downloads/ から最新版をダウンロード
2. インストール時に **"Add Python to PATH"** にチェック
3. インストール完了後、PowerShellで確認：

```powershell
python --version
# Python 3.x.x と表示されればOK
```

### 依存ライブラリのインストール

```powershell
cd C:\Users\world\OneDrive\デスクトップ\ObsidianManager
pip install -r requirements.txt
```

---

## 2. Git for Windows のセットアップ

### Git インストール

1. https://git-scm.com/download/win からダウンロード
2. デフォルト設定でインストール

### Git 設定

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## 3. Obsidian のセットアップ

### Obsidian インストール

1. https://obsidian.md/ からダウンロード
2. インストール

### Vault 設定

1. Obsidianを起動
2. "Open folder as vault" を選択
3. **重要**: `C:\Users\world\OneDrive\デスクトップ\ObsidianManager\ObsidianVault` を選択
4. Vaultが開いたら設定を確認

### プラグイン有効化

既に有効化されているプラグイン：
- ✅ Dataview
- ✅ Templater
- ✅ Advanced Tables
- ✅ Git
- ✅ Tag Wrangler
- ✅ CSS Snippets

追加の設定は不要です。

---

## 4. システムの使い方（Windows版）

### 論文追加

#### PowerShellから実行

```powershell
# 対話的入力
python scripts\add_paper.py --pdf "C:\path\to\paper.pdf"

# YAMLから
python scripts\add_paper.py `
  --pdf "C:\path\to\paper.pdf" `
  --metadata "C:\path\to\metadata.yaml"
```

**注意**: Windowsではパスの区切りが `\`（バックスラッシュ）です。

#### パスの指定方法

```powershell
# 絶対パス（推奨）
python scripts\add_paper.py --pdf "C:\Users\world\Downloads\paper.pdf"

# 相対パス
python scripts\add_paper.py --pdf "..\..\Downloads\paper.pdf"

# スペースを含むパス（ダブルクォートで囲む）
python scripts\add_paper.py --pdf "C:\Users\world\OneDrive\My Papers\paper.pdf"
```

### タグ管理

```powershell
# タグ一覧
python scripts\tag_manager.py list

# 新しいタグ追加
python scripts\tag_manager.py add disease alzheimer --aliases "AD"

# 統計情報
python scripts\tag_manager.py stats
```

### エクスポート

```powershell
# 選択ノートからエクスポート
python scripts\export_selected.py `
  "ObsidianVault\selection.md" `
  "exports\my_project"
```

---

## 5. Windowsパス対応の注意点

### config.yaml の調整

`config/config.yaml`でパスを設定する場合：

```yaml
# Windowsの場合
paths:
  papers_dir: C:/Users/world/OneDrive/デスクトップ/ObsidianManager/papers/all_papers
  obsidian_vault: C:/Users/world/OneDrive/デスクトップ/ObsidianManager/ObsidianVault
  # ...
```

**ポイント**:
- YAMLファイルでは `/`（スラッシュ）を使用
- バックスラッシュ `\` を使う場合は `\\` とエスケープ

### PDFパスの記録

論文追加時、PDFパスは自動的に絶対パスで記録されます：

```
C:\Users\world\OneDrive\デスクトップ\ObsidianManager\papers\all_papers\paper001.pdf
```

Obsidianでファイルリンクとして開けます。

---

## 6. トラブルシューティング

### Python が見つからない

```powershell
# Pythonのパスを確認
where python

# 出力がない場合はPATH環境変数を確認
# システム環境変数にPythonのパスを追加
```

### Git コマンドが使えない

```powershell
# Gitのパスを確認
where git

# Git for Windowsを再インストール
```

### Obsidian でDataviewが動かない

1. Settings → Community plugins → Turn on
2. Browse → "Dataview" → Install → Enable
3. Obsidianを再起動

### PDF が開けない

- PDFパスが正しいか確認
- OneDriveの同期状態を確認
- ファイルが実際に存在するか確認

### 日本語ファイル名の問題

```powershell
# Git で日本語ファイル名を扱う設定
git config --global core.quotepath false
```

---

## 7. OneDrive との連携

### メリット

- 自動バックアップ
- 複数デバイス間で同期
- クラウドストレージ

### 注意点

1. **PDFの同期**
   - PDFファイルは `.gitignore` で除外されています
   - OneDriveで自動同期されます

2. **競合の解決**
   - 複数デバイスで同時編集すると競合が発生する可能性
   - Obsidian Gitプラグインで自動プル・プッシュを有効化

3. **同期のタイミング**
   - OneDriveの同期が完了してからGit操作を推奨

---

## 8. ショートカット設定（オプション）

### PowerShell スクリプト作成

`add_paper.ps1`:

```powershell
# 論文追加スクリプト
param(
    [string]$pdf
)

Set-Location "C:\Users\world\OneDrive\デスクトップ\ObsidianManager"
python scripts\add_paper.py --pdf $pdf
```

使い方：

```powershell
.\add_paper.ps1 -pdf "C:\path\to\paper.pdf"
```

---

## 9. よくある質問（Windows版）

### Q: PowerShellでコマンドが長い

A: バッククォート `` ` `` で改行できます：

```powershell
python scripts\export_selected.py `
  "ObsidianVault\selection.md" `
  "exports\my_project"
```

### Q: ダブルクリックでスクリプト実行できる？

A: `.bat` ファイルを作成：

```batch
@echo off
cd /d C:\Users\world\OneDrive\デスクトップ\ObsidianManager
python scripts\add_paper.py
pause
```

### Q: Pythonスクリプトが文字化けする

A: スクリプトファイルがUTF-8で保存されているか確認

---

## 10. 次のステップ

- [README.md](../README.md) - システム概要
- [USAGE.md](USAGE.md) - 詳細な使い方
- [仕様書](SPECIFICATION.md) - 仕様詳細

---

**Last Updated**: 2024-11-24
