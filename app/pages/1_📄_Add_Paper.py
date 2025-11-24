"""
論文追加ページ
"""

import streamlit as st
import sys
from pathlib import Path
import json
import shutil
from datetime import datetime
import yaml

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils import PDFProcessor, TagSystem, GitManager

# ページ設定
st.set_page_config(page_title="論文追加", page_icon="📄", layout="wide")

# 初期化
@st.cache_resource
def init_system():
    """システムコンポーネントを初期化"""
    tag_hierarchy_path = project_root / "data" / "tag_hierarchy.json"
    tag_groups_path = project_root / "data" / "tag_groups.json"

    pdf_processor = PDFProcessor()
    tag_system = TagSystem(tag_hierarchy_path, tag_groups_path)

    return pdf_processor, tag_system

pdf_processor, tag_system = init_system()

# タイトル
st.title("📄 新しい論文を追加")

st.markdown("---")

# 2カラムレイアウト
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("1️⃣ PDFファイル")

    # PDFアップロード
    uploaded_file = st.file_uploader(
        "PDFファイルをアップロード",
        type=['pdf'],
        help="論文のPDFファイルをドラッグ&ドロップまたは選択してください"
    )

    if uploaded_file:
        st.success(f"✓ {uploaded_file.name} が選択されました")

        # PDF情報表示
        file_size = uploaded_file.size / 1024 / 1024  # MB
        st.info(f"ファイルサイズ: {file_size:.2f} MB")

with col_right:
    st.subheader("2️⃣ 基本情報")

    # タイトル
    title = st.text_input(
        "論文タイトル *",
        placeholder="例: 脳卒中患者の歩行パターン解析...",
        help="論文の正式なタイトル"
    )

    # 著者
    authors_str = st.text_input(
        "著者（カンマ区切り） *",
        placeholder="例: Yamada T, Suzuki K, Tanaka M",
        help="著者名をカンマで区切って入力"
    )

    # 年・ジャーナル
    col_year, col_journal = st.columns(2)

    with col_year:
        year = st.number_input(
            "出版年 *",
            min_value=1900,
            max_value=2100,
            value=2024,
            step=1
        )

    with col_journal:
        journal = st.text_input(
            "ジャーナル名 *",
            placeholder="例: Journal of Biomechanics"
        )

    # 巻・号・ページ
    col_vol, col_issue, col_pages = st.columns(3)

    with col_vol:
        volume = st.text_input("巻", placeholder="45")

    with col_issue:
        issue = st.text_input("号", placeholder="3")

    with col_pages:
        pages = st.text_input("ページ", placeholder="123-135")

    # DOI・PMID
    col_doi, col_pmid = st.columns(2)

    with col_doi:
        doi = st.text_input(
            "DOI",
            placeholder="10.1234/journal.2024.001",
            help="Digital Object Identifier"
        )

    with col_pmid:
        pmid = st.text_input(
            "PMID",
            placeholder="12345678",
            help="PubMed ID"
        )

st.markdown("---")

# 研究デザイン
st.subheader("3️⃣ 研究デザイン")

col_design1, col_design2 = st.columns(2)

with col_design1:
    # 研究タイプ（必須）
    study_types = tag_system.get_canonical_tags('study_type')
    study_type = st.selectbox(
        "研究タイプ *",
        options=study_types,
        help="研究デザインのタイプ（必須）"
    )

    # サンプルサイズ
    sample_size = st.number_input(
        "サンプルサイズ",
        min_value=0,
        value=0,
        step=1,
        help="研究の対象者数"
    )

with col_design2:
    # 研究デザイン詳細
    study_design = st.text_input(
        "研究デザイン詳細",
        placeholder="例: 横断研究、多施設共同研究",
        help="研究デザインの詳しい説明"
    )

    # 対象集団
    study_population = st.text_area(
        "対象集団",
        placeholder="例: 脳卒中患者（発症後6ヶ月以上、平均年齢68.5歳）",
        help="研究対象の詳細"
    )

st.markdown("---")

# 分類（Perspectives）
st.subheader("4️⃣ 分類（Perspectives）")

col_p1, col_p2 = st.columns(2)

with col_p1:
    # Disease
    diseases = ["not_applicable"] + tag_system.get_canonical_tags('disease')
    disease = st.selectbox(
        "Disease（疾患・病態）",
        options=diseases,
        help="研究対象の疾患"
    )

    # Method
    methods = ["not_applicable"] + tag_system.get_canonical_tags('method')
    method = st.selectbox(
        "Method（測定・評価方法）",
        options=methods,
        help="使用した測定・評価方法"
    )

with col_p2:
    # Analysis
    analyses = ["not_applicable"] + tag_system.get_canonical_tags('analysis')
    analysis = st.selectbox(
        "Analysis（解析手法）",
        options=analyses,
        help="データ解析の手法"
    )

    # Population
    populations = ["not_applicable"] + tag_system.get_canonical_tags('population')
    population = st.selectbox(
        "Population（対象集団）",
        options=populations,
        help="研究対象の年齢層など"
    )

st.markdown("---")

# その他
st.subheader("5️⃣ その他")

# キーワード
keywords_str = st.text_input(
    "キーワード（カンマ区切り）",
    placeholder="例: stroke, gait analysis, machine learning",
    help="論文のキーワード"
)

# 言語
language = st.selectbox(
    "言語",
    options=["en", "ja", "other"],
    help="論文の言語"
)

# 優先度
priority = st.select_slider(
    "優先度",
    options=["low", "medium", "high"],
    value="medium"
)

# アブストラクト
abstract = st.text_area(
    "Abstract（原文）",
    placeholder="論文のアブストラクトを貼り付けてください...",
    height=150,
    help="論文のアブストラクト（オプション）"
)

# 要約
summary = st.text_area(
    "要約（日本語）",
    placeholder="目的:\n\n方法:\n\n結果:\n\n結論:",
    height=150,
    help="日本語での簡潔な要約（オプション）"
)

st.markdown("---")

# 追加ボタン
col_submit, col_preview = st.columns([1, 1])

with col_submit:
    if st.button("📝 論文を追加", type="primary", use_container_width=True):
        # バリデーション
        if not title:
            st.error("❌ タイトルは必須です")
        elif not authors_str:
            st.error("❌ 著者は必須です")
        elif not journal:
            st.error("❌ ジャーナル名は必須です")
        elif not uploaded_file:
            st.error("❌ PDFファイルをアップロードしてください")
        else:
            try:
                with st.spinner("論文を追加中..."):
                    # Paper ID生成
                    catalog_path = project_root / "data" / "catalog.json"
                    with open(catalog_path, 'r', encoding='utf-8') as f:
                        catalog = json.load(f)

                    existing_ids = list(catalog['papers'].keys())
                    if not existing_ids:
                        paper_id = "paper001"
                    else:
                        max_num = max([int(pid.replace("paper", ""))
                                     for pid in existing_ids
                                     if pid.startswith("paper")])
                        paper_id = f"paper{str(max_num + 1).zfill(3)}"

                    # PDFを保存
                    papers_dir = project_root / "papers" / "all_papers"
                    papers_dir.mkdir(parents=True, exist_ok=True)

                    pdf_dest = papers_dir / f"{paper_id}.pdf"
                    with open(pdf_dest, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # メタデータ作成
                    authors_list = [a.strip() for a in authors_str.split(',') if a.strip()]
                    keywords_list = [k.strip() for k in keywords_str.split(',') if k.strip()] if keywords_str else []

                    perspectives = {
                        'study_type': study_type,
                        'disease': disease,
                        'method': method,
                        'analysis': analysis,
                        'population': population
                    }

                    # タグ正規化
                    perspectives = tag_system.normalize_tags(perspectives)

                    now = datetime.now().isoformat()

                    metadata = {
                        'paper_id': paper_id,
                        'title': title,
                        'authors': authors_list,
                        'year': year,
                        'journal': journal,
                        'volume': volume,
                        'issue': issue,
                        'pages': pages,
                        'doi': doi,
                        'pmid': pmid,
                        'pdf_path': str(pdf_dest.absolute()),
                        'study_type': study_type,
                        'study_design': study_design,
                        'sample_size': sample_size if sample_size > 0 else None,
                        'study_population': study_population,
                        'perspectives': perspectives,
                        'keywords': keywords_list,
                        'language': language,
                        'priority': priority,
                        'abstract': abstract,
                        'summary': summary,
                        'date_added': now,
                        'date_modified': now,
                        'read_status': 'unread'
                    }

                    # catalog.jsonに追加
                    catalog['papers'][paper_id] = metadata

                    # メタデータ統計を更新
                    catalog['metadata']['total_papers'] = len(catalog['papers'])
                    catalog['metadata']['last_updated'] = now

                    # 分布を更新
                    for dist_key in ['study_type', 'disease', 'method', 'analysis', 'population']:
                        distribution = {}
                        for paper_data in catalog['papers'].values():
                            perspectives_data = paper_data.get('perspectives', {})
                            if dist_key in perspectives_data:
                                tag = perspectives_data[dist_key]
                                if tag and tag != "not_applicable":
                                    distribution[tag] = distribution.get(tag, 0) + 1
                        catalog['metadata'][f'{dist_key}_distribution'] = distribution

                    # 保存
                    with open(catalog_path, 'w', encoding='utf-8') as f:
                        json.dump(catalog, f, indent=2, ensure_ascii=False)

                    # Obsidianノート生成（簡易版）
                    from scripts.add_paper import PaperAdder
                    import yaml

                    config_path = project_root / "config" / "config.yaml"
                    adder = PaperAdder(config_path)

                    # ノート生成
                    adder._create_obsidian_note(paper_id, metadata)
                    adder._update_moc_notes(metadata)

                    st.success(f"✅ 論文を追加しました: {paper_id}")
                    st.balloons()

                    # Obsidianで開くリンク
                    obsidian_note_path = project_root / "ObsidianVault" / "Papers" / f"{paper_id}.md"
                    obsidian_uri = f"obsidian://open?path={obsidian_note_path.absolute()}"

                    st.markdown(f"""
                    ### 🎉 追加完了！

                    **Paper ID**: `{paper_id}`

                    **次のステップ**:
                    - [📖 Obsidianで開く]({obsidian_uri})
                    - [📚 一覧ページで確認](Browse)
                    """)

            except Exception as e:
                st.error(f"❌ エラーが発生しました: {e}")
                import traceback
                st.code(traceback.format_exc())

with col_preview:
    if st.button("👁️ プレビュー", use_container_width=True):
        st.session_state.show_preview = True

# プレビュー表示
if st.session_state.get('show_preview', False):
    st.markdown("---")
    st.subheader("📋 入力内容プレビュー")

    preview_data = {
        "タイトル": title,
        "著者": authors_str,
        "年": year,
        "ジャーナル": journal,
        "研究タイプ": study_type,
        "Disease": disease,
        "Method": method,
        "Analysis": analysis,
        "Population": population
    }

    for key, value in preview_data.items():
        if value:
            st.write(f"**{key}**: {value}")
