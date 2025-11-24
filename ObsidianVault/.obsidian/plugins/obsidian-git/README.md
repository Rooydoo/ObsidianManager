# Obsidian Git Plugin 設定

## 機能

- 自動バックアップ（10分ごと）
- 自動プル（起動時 + 10分ごと）
- ステータスバー表示
- 変更ファイルリスト表示

## 使い方

### 手動コミット

1. Ctrl/Cmd + P でコマンドパレットを開く
2. "Git: Commit all changes" を選択
3. コミットメッセージを入力

### 手動プッシュ

1. Ctrl/Cmd + P
2. "Git: Push" を選択

### 手動プル

1. Ctrl/Cmd + P
2. "Git: Pull" を選択

## 設定

Settings → Obsidian Git で設定を変更できます：

- **Auto backup interval**: 自動バックアップの間隔（分）
- **Auto pull interval**: 自動プルの間隔（分）
- **Disable push**: プッシュを無効化（ローカルのみで使う場合）
- **Pull before push**: プッシュ前に必ずプルする

## トラブルシューティング

### プッシュが失敗する

- GitHubの認証情報を確認
- リモートリポジトリのURLを確認
- `.gitignore`で除外されていないか確認

### 競合が発生した

1. 手動でマージする
2. または "Git: Pull (rebase)" を使用

---

**Note**: システムのPythonスクリプトでも自動コミット機能があります。
両方を併用する場合は、自動バックアップ間隔を調整してください。
