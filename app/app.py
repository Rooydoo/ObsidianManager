"""
医学論文管理システム - Streamlit UI

Obsidianと連携した論文管理の入力・管理インターフェース
"""

import streamlit as st
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# ページ設定
st.set_page_config(
    page_title="医学論文管理システム",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .obsidian-link {
        background-color: #7c3aed;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.3rem;
        text-decoration: none;
        display: inline-block;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# サイドバー
with st.sidebar:
    st.image("https://obsidian.md/images/obsidian-logo-gradient.svg", width=50)
    st.title("📚 論文管理")

    st.markdown("---")

    # システム情報
    try:
        import json
        catalog_path = project_root / "data" / "catalog.json"
        with open(catalog_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)

        total_papers = catalog['metadata']['total_papers']
        st.metric("総論文数", total_papers)

        # 研究タイプ分布
        study_types = catalog['metadata'].get('study_type_distribution', {})
        if study_types:
            top_type = max(study_types, key=study_types.get)
            st.metric("最多研究タイプ", f"{top_type} ({study_types[top_type]}件)")

    except Exception as e:
        st.warning("データ読み込みエラー")

    st.markdown("---")

    # Obsidian連携
    st.subheader("🔗 Obsidian")

    vault_path = project_root / "ObsidianVault"

    # Obsidianプロトコルリンク
    obsidian_uri = f"obsidian://open?path={vault_path.absolute()}"

    st.markdown(f"""
    <a href="{obsidian_uri}" class="obsidian-link" target="_blank">
        📖 Obsidian Vaultを開く
    </a>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ヘルプ
    st.subheader("💡 ヘルプ")
    st.markdown("""
    **使い方**:
    1. 📄 論文追加で新規登録
    2. 📚 一覧で論文を検索
    3. 📊 統計で全体像を把握
    4. 🔗 Obsidianで深く探索
    """)

# メインコンテンツ
st.markdown('<div class="main-header">📚 医学論文管理システム</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Obsidian連携型 論文データベース</div>', unsafe_allow_html=True)

# ウェルカムメッセージ
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="info-box">
        <h3>📄 論文追加</h3>
        <p>PDFをアップロードして<br>メタデータを入力</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-box">
        <h3>📚 論文一覧</h3>
        <p>フィルタ・検索で<br>論文を探す</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="info-box">
        <h3>📊 統計分析</h3>
        <p>研究の全体像を<br>可視化</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# クイックスタート
st.subheader("🚀 クイックスタート")

tab1, tab2, tab3 = st.tabs(["新規ユーザー", "論文追加", "Obsidian連携"])

with tab1:
    st.markdown("""
    ### 👋 初めての方へ

    このシステムは2つの要素で構成されています：

    1. **Streamlit UI（このアプリ）**
       - 論文の追加・管理
       - 一覧表示・統計
       - データ入力の簡素化

    2. **Obsidian**
       - 論文の閲覧・探索
       - ネットワークグラフ
       - メモ・リンク

    **おすすめの使い方**:
    1. ←サイドバーの「📖 Obsidian Vaultを開く」でObsidianを起動
    2. 左メニューから「📄 論文追加」で論文を登録
    3. Obsidianで論文を読みながらメモ
    """)

with tab2:
    st.markdown("""
    ### 📝 論文追加の流れ

    1. 左メニューから「📄 Add Paper」を選択
    2. PDFファイルをアップロード
    3. フォームに基本情報を入力
       - タイトル、著者、年
       - 研究タイプ（必須）
       - 分類（Disease, Method, Analysis）
    4. 「追加」ボタンをクリック
    5. Obsidianで自動生成されたノートを確認
    """)

with tab3:
    st.markdown("""
    ### 🔗 Obsidianとの連携

    **このアプリの役割**:
    - データ入力（論文追加）
    - 統計・一覧表示
    - フィルタ検索

    **Obsidianの役割**:
    - 論文ノートの閲覧
    - グラフビューでネットワーク探索
    - Dataviewで動的クエリ
    - メモ・リンク・タグ付け

    **連携方法**:
    - 一覧画面の各論文に「Obsidianで開く」ボタン
    - クリックで該当ノートを直接開く
    - Obsidian内での編集は自動保存
    """)

st.markdown("---")

# 最近追加された論文
st.subheader("📝 最近追加された論文")

try:
    import pandas as pd

    papers = catalog['papers']
    if papers:
        # 最新5件を表示
        papers_list = []
        for paper_id, paper_data in list(papers.items())[-5:]:
            papers_list.append({
                'ID': paper_id,
                'タイトル': paper_data.get('title', 'N/A'),
                '著者': ', '.join(paper_data.get('authors', [])[:2]),
                '年': paper_data.get('year', 'N/A'),
                '研究タイプ': paper_data.get('study_type', 'N/A')
            })

        df = pd.DataFrame(papers_list)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("まだ論文が登録されていません。左メニューから「📄 Add Paper」で追加してください。")

except Exception as e:
    st.error(f"データ読み込みエラー: {e}")

# フッター
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.9rem;">
    医学論文管理システム v1.0 | Powered by Streamlit + Obsidian
</div>
""", unsafe_allow_html=True)
