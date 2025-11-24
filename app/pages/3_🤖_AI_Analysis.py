"""
AI自動解析ページ（Phase 2）

PDFから自動的にメタデータを抽出・生成
Claude APIなどを使用した完全自動化
"""

import streamlit as st
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# ページ設定
st.set_page_config(page_title="AI自動解析", page_icon="🤖", layout="wide")

# タイトル
st.title("🤖 AI自動解析（Phase 2）")

st.markdown("""
PDFをアップロードするだけで、AIが自動的に：
- アブストラクトを抽出
- メタデータを生成
- タグを推薦
- 要約を作成

完全自動で論文を追加できます。
""")

st.markdown("---")

# Phase 2 準備中メッセージ
st.info("🚧 **Phase 2で実装予定の機能です**")

# 機能プレビュー
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 予定機能")

    st.markdown("""
    ### 自動抽出
    - ✅ PDFからアブストラクト抽出
    - ✅ タイトル・著者・年の検出
    - ✅ DOI/PMIDの検出

    ### AI生成
    - 🤖 Claude APIで日本語要約生成
    - 🤖 研究タイプの自動判定
    - 🤖 Disease/Method/Analysisタグの推薦
    - 🤖 キーワード抽出

    ### ワンクリック追加
    - 🎉 確認画面でOKするだけ
    - 🎉 手動修正も可能
    """)

with col2:
    st.subheader("⚙️ 設定")

    st.markdown("### Claude API設定")

    api_key = st.text_input(
        "API Key",
        type="password",
        help="Anthropic Claude APIキー",
        disabled=True,
        placeholder="Phase 2で有効化されます"
    )

    model = st.selectbox(
        "モデル",
        options=["claude-sonnet-4-20250514", "claude-opus-4-20250514"],
        disabled=True
    )

    st.markdown("### 処理オプション")

    st.checkbox("アブストラクトを自動抽出", value=True, disabled=True)
    st.checkbox("要約を自動生成", value=True, disabled=True)
    st.checkbox("タグを自動推薦", value=True, disabled=True)

st.markdown("---")

# デモUI（非機能）
st.subheader("📄 PDFアップロード（プレビュー）")

uploaded_file = st.file_uploader(
    "PDFファイルをアップロード",
    type=['pdf'],
    help="Phase 2で有効化されます",
    disabled=True
)

col_demo1, col_demo2 = st.columns([1, 1])

with col_demo1:
    if st.button("🤖 AI解析を実行", disabled=True, use_container_width=True):
        pass

with col_demo2:
    if st.button("📝 手動編集モード", disabled=True, use_container_width=True):
        pass

st.markdown("---")

# 実装予定の流れ
st.subheader("🔄 実装予定のワークフロー")

st.markdown("""
```
1. PDFアップロード
     ↓
2. PDF解析
   - pdfplumberでテキスト抽出
   - アブストラクトセクション検出
   - メタデータ抽出（タイトル、著者、DOI等）
     ↓
3. Claude API呼び出し
   - プロンプト送信
   - メタデータ生成
   - 要約生成
   - タグ推薦
     ↓
4. プレビュー画面
   - 生成されたメタデータ表示
   - 手動修正可能
   - 信頼度スコア表示
     ↓
5. 確認＆追加
   - ワンクリックで追加
   - Obsidianノート自動生成
   - Git自動コミット
```
""")

st.markdown("---")

# 技術仕様（開発者向け）
with st.expander("🔧 技術仕様（開発者向け）"):
    st.markdown("""
    ### 実装予定の技術スタック

    **PDF処理**:
    ```python
    from scripts.utils import PDFProcessor

    processor = PDFProcessor()
    text = processor.extract_text(pdf_path)
    abstract = processor.extract_abstract(pdf_path)
    ```

    **Claude API統合**:
    ```python
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"Extract metadata from: {abstract}"}
        ]
    )

    metadata = parse_claude_response(response.content[0].text)
    ```

    **プロンプト**:
    - `scripts/prompts/metadata_generation_prompt.txt` を使用
    - アブストラクト + 論文情報を送信
    - 構造化JSON形式で受信

    **エラーハンドリング**:
    - APIエラー時は手動モードにフォールバック
    - 信頼度スコアが低い場合は警告表示
    - タグが未知の場合は新規タグとして提案

    ### 設定ファイル

    `config/config.yaml`:
    ```yaml
    ai:
      enabled: true
      provider: claude
      model: claude-sonnet-4-20250514
      api_key_file: ./config/api_keys.env
    ```

    ### 実装ファイル

    作成予定:
    - `scripts/ai_analyzer.py` - AI解析エンジン
    - `config/api_keys.env` - APIキー管理
    - `scripts/prompts/auto_analysis_prompt.txt` - 自動解析用プロンプト
    """)

# フィードバック
st.markdown("---")
st.subheader("💬 フィードバック")

st.markdown("""
Phase 2の実装に向けて、以下の機能についてご意見をお聞かせください：

- 必要な自動抽出項目
- AIに期待する精度
- 手動修正の必要性
- その他の要望
""")

feedback = st.text_area(
    "フィードバックを入力",
    placeholder="Phase 2で実装してほしい機能や改善点...",
    height=100,
    disabled=True
)

if st.button("フィードバックを送信", disabled=True):
    st.success("ありがとうございます！（Phase 2で実装時に参考にします）")

st.markdown("---")

# ステータス
st.info("""
**現在のステータス**: Phase 2準備中

**Phase 1（現在利用可能）**:
- ✅ 手動フォーム入力（Add Paper）
- ✅ メタデータファイルアップロード（Add from Metadata）
- ✅ 一覧・検索（Browse）
- ✅ 統計（Statistics）

**Phase 2（開発予定）**:
- 🚧 AI自動解析（このページ）
- 🚧 Claude API統合
- 🚧 バッチ処理
- 🚧 推薦システム
""")
