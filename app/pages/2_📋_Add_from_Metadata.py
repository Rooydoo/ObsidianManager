"""
メタデータファイルからの論文追加ページ

Claude Webなどで生成したメタデータファイル（JSON/YAML/MD）とPDFを同時アップロード
"""

import streamlit as st
import sys
from pathlib import Path
import json
import yaml
from datetime import datetime
import re

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils import PDFProcessor, TagSystem, GitManager

# ページ設定
st.set_page_config(page_title="メタデータから追加", page_icon="📋", layout="wide")

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
st.title("📋 メタデータファイルから追加")

st.markdown("""
Claude WebなどのAIで生成したメタデータファイルとPDFを同時にアップロードして追加します。

**対応フォーマット**: JSON, YAML, Markdown
""")

st.markdown("---")

# ファイルアップロードセクション
col_pdf, col_metadata = st.columns(2)

with col_pdf:
    st.subheader("1️⃣ PDFファイル")
    uploaded_pdf = st.file_uploader(
        "論文PDFをアップロード",
        type=['pdf'],
        help="論文のPDFファイル"
    )

    if uploaded_pdf:
        st.success(f"✓ {uploaded_pdf.name}")
        file_size = uploaded_pdf.size / 1024 / 1024
        st.info(f"ファイルサイズ: {file_size:.2f} MB")

with col_metadata:
    st.subheader("2️⃣ メタデータファイル")
    uploaded_metadata = st.file_uploader(
        "メタデータファイルをアップロード",
        type=['json', 'yaml', 'yml', 'md', 'txt'],
        help="Claude Webなどで生成したメタデータファイル"
    )

    if uploaded_metadata:
        st.success(f"✓ {uploaded_metadata.name}")

st.markdown("---")

# メタデータパース関数
def parse_json(content: str) -> dict:
    """JSONをパース"""
    return json.loads(content)

def parse_yaml(content: str) -> dict:
    """YAMLをパース"""
    # YAMLフロントマターを抽出（Markdownの場合）
    if content.strip().startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            yaml_content = parts[1]
            return yaml.safe_load(yaml_content)

    return yaml.safe_load(content)

def parse_markdown(content: str) -> dict:
    """Markdownからメタデータを抽出"""
    # YAMLフロントマターがあればそれを使う
    if content.strip().startswith('---'):
        return parse_yaml(content)

    # フロントマターがない場合は簡易パース
    metadata = {}

    # タイトル
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        metadata['title'] = title_match.group(1)

    # キーワード的な情報を抽出
    lines = content.split('\n')
    for line in lines:
        if ':' in line and not line.strip().startswith('#'):
            key, value = line.split(':', 1)
            key = key.strip().lower().replace(' ', '_')
            value = value.strip()
            metadata[key] = value

    return metadata

def parse_metadata_file(file) -> dict:
    """メタデータファイルをパース"""
    content = file.read().decode('utf-8')
    file_name = file.name.lower()

    try:
        if file_name.endswith('.json'):
            return parse_json(content)
        elif file_name.endswith(('.yaml', '.yml')):
            return parse_yaml(content)
        elif file_name.endswith(('.md', '.txt')):
            return parse_markdown(content)
        else:
            st.error(f"未対応のファイル形式: {file_name}")
            return {}
    except Exception as e:
        st.error(f"パースエラー: {e}")
        return {}

# メタデータ表示・編集
if uploaded_metadata:
    st.subheader("3️⃣ メタデータプレビュー")

    # パース実行
    metadata = parse_metadata_file(uploaded_metadata)

    if metadata:
        # タブで表示切り替え
        tab_json, tab_edit = st.tabs(["📄 プレビュー", "✏️ 編集"])

        with tab_json:
            st.json(metadata)

        with tab_edit:
            st.markdown("**必要に応じて修正してください**")

            # 主要フィールドを編集可能に
            col_e1, col_e2 = st.columns(2)

            with col_e1:
                metadata['title'] = st.text_input(
                    "タイトル",
                    value=metadata.get('title', ''),
                    key='edit_title'
                )

                authors_str = ', '.join(metadata.get('authors', [])) if isinstance(metadata.get('authors'), list) else metadata.get('authors', '')
                authors_input = st.text_input(
                    "著者（カンマ区切り）",
                    value=authors_str,
                    key='edit_authors'
                )
                metadata['authors'] = [a.strip() for a in authors_input.split(',') if a.strip()]

                metadata['year'] = st.number_input(
                    "年",
                    value=int(metadata.get('year', 2024)) if metadata.get('year') else 2024,
                    min_value=1900,
                    max_value=2100,
                    key='edit_year'
                )

                metadata['journal'] = st.text_input(
                    "ジャーナル",
                    value=metadata.get('journal', ''),
                    key='edit_journal'
                )

            with col_e2:
                # 研究タイプ
                study_types = tag_system.get_canonical_tags('study_type')
                current_study_type = metadata.get('study_type', study_types[0])
                if current_study_type not in study_types:
                    study_types.insert(0, current_study_type)

                metadata['study_type'] = st.selectbox(
                    "研究タイプ",
                    options=study_types,
                    index=study_types.index(current_study_type) if current_study_type in study_types else 0,
                    key='edit_study_type'
                )

                # Perspectives
                if 'perspectives' not in metadata:
                    metadata['perspectives'] = {}

                diseases = ["not_applicable"] + tag_system.get_canonical_tags('disease')
                current_disease = metadata.get('perspectives', {}).get('disease', 'not_applicable')
                if current_disease and current_disease not in diseases:
                    diseases.insert(1, current_disease)

                metadata['perspectives']['disease'] = st.selectbox(
                    "Disease",
                    options=diseases,
                    index=diseases.index(current_disease) if current_disease in diseases else 0,
                    key='edit_disease'
                )

                methods = ["not_applicable"] + tag_system.get_canonical_tags('method')
                current_method = metadata.get('perspectives', {}).get('method', 'not_applicable')
                if current_method and current_method not in methods:
                    methods.insert(1, current_method)

                metadata['perspectives']['method'] = st.selectbox(
                    "Method",
                    options=methods,
                    index=methods.index(current_method) if current_method in methods else 0,
                    key='edit_method'
                )

st.markdown("---")

# 追加ボタン
if uploaded_pdf and uploaded_metadata and metadata:
    col_btn1, col_btn2 = st.columns([1, 3])

    with col_btn1:
        if st.button("📝 論文を追加", type="primary", use_container_width=True):
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
                        f.write(uploaded_pdf.getbuffer())

                    # メタデータを整形
                    metadata['paper_id'] = paper_id
                    metadata['pdf_path'] = str(pdf_dest.absolute())

                    # perspectives.study_type を設定
                    if 'perspectives' not in metadata:
                        metadata['perspectives'] = {}
                    metadata['perspectives']['study_type'] = metadata.get('study_type', '')

                    # タグ正規化
                    metadata['perspectives'] = tag_system.normalize_tags(metadata['perspectives'])

                    # タイムスタンプ
                    now = datetime.now().isoformat()
                    metadata['date_added'] = now
                    metadata['date_modified'] = now

                    # デフォルト値
                    if 'read_status' not in metadata:
                        metadata['read_status'] = 'unread'
                    if 'priority' not in metadata:
                        metadata['priority'] = 'medium'
                    if 'language' not in metadata:
                        metadata['language'] = 'en'

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

                    # Obsidianノート生成
                    from scripts.add_paper import PaperAdder

                    config_path = project_root / "config" / "config.yaml"
                    adder = PaperAdder(config_path)
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

else:
    st.info("📤 PDFファイルとメタデータファイルの両方をアップロードしてください")

# 使い方ガイド
st.markdown("---")
st.subheader("💡 使い方")

with st.expander("Claude Webでメタデータを生成する方法"):
    st.markdown("""
    ### 1. プロンプトを使用

    `scripts/prompts/metadata_generation_prompt.txt` の内容をClaude Webに貼り付け

    ### 2. 論文情報を入力

    タイトル、著者、アブストラクトなどを入力

    ### 3. アーティファクトをダウンロード

    生成されたYAML/JSONをファイルとして保存

    ### 4. このページでアップロード

    PDFとメタデータファイルを同時にアップロード
    """)

with st.expander("対応フォーマット"):
    st.markdown("""
    ### JSON形式
    ```json
    {
      "title": "論文タイトル",
      "authors": ["著者1", "著者2"],
      "year": 2024,
      "study_type": "rct",
      "perspectives": {
        "disease": "stroke",
        "method": "gait_analysis"
      }
    }
    ```

    ### YAML形式
    ```yaml
    ---
    title: 論文タイトル
    authors:
      - 著者1
      - 著者2
    year: 2024
    study_type: rct
    perspectives:
      disease: stroke
      method: gait_analysis
    ---
    ```

    ### Markdown形式（YAMLフロントマター付き）
    ```markdown
    ---
    title: 論文タイトル
    authors: [著者1, 著者2]
    year: 2024
    ---

    # 論文タイトル

    内容...
    ```
    """)
