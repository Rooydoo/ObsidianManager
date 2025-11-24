"""
論文一覧・検索ページ
"""

import streamlit as st
import sys
from pathlib import Path
import json
import pandas as pd
import zipfile
import io
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# ページ設定
st.set_page_config(page_title="論文一覧", page_icon="📚", layout="wide")

# データ読み込み
@st.cache_data
def load_catalog():
    """カタログデータを読み込み"""
    catalog_path = project_root / "data" / "catalog.json"
    with open(catalog_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_papers_zip(selected_ids, papers, project_root):
    """
    選択された論文のPDFとメタデータをZIPファイルにまとめる

    Args:
        selected_ids: 選択された論文IDのリスト
        papers: 全論文データ
        project_root: プロジェクトルート

    Returns:
        BytesIO: ZIPファイルのバイナリデータ
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 選択された論文のカタログデータ
        export_catalog = {
            'papers': {},
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'total_papers': len(selected_ids),
                'exported_by': 'ObsidianManager'
            }
        }

        for paper_id in selected_ids:
            if paper_id not in papers:
                continue

            paper_data = papers[paper_id]
            export_catalog['papers'][paper_id] = paper_data

            # PDFファイルを追加
            pdf_path = paper_data.get('pdf_path')
            if pdf_path and Path(pdf_path).exists():
                pdf_file_path = Path(pdf_path)
                zip_file.write(
                    pdf_file_path,
                    arcname=f"papers/{pdf_file_path.name}"
                )

            # メタデータJSONを追加
            metadata_json = json.dumps(paper_data, ensure_ascii=False, indent=2)
            zip_file.writestr(
                f"metadata/{paper_id}.json",
                metadata_json
            )

        # カタログファイルを追加
        catalog_json = json.dumps(export_catalog, ensure_ascii=False, indent=2)
        zip_file.writestr("catalog_export.json", catalog_json)

        # READMEを追加
        readme_content = f"""# 論文エクスポート

エクスポート日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
論文数: {len(selected_ids)}件

## フォルダ構成

- papers/ : PDFファイル
- metadata/ : 各論文のメタデータ（JSON形式）
- catalog_export.json : 選択した論文のカタログ情報

## ObsidianManagerについて

このファイルはObsidianManagerからエクスポートされました。
リポジトリ: https://github.com/Rooydoo/ObsidianManager
"""
        zip_file.writestr("README.md", readme_content)

    zip_buffer.seek(0)
    return zip_buffer

# タイトル
st.title("📚 論文一覧・検索")

try:
    catalog = load_catalog()
    papers = catalog['papers']

    if not papers:
        st.info("📭 まだ論文が登録されていません。「📄 Add Paper」から追加してください。")
        st.stop()

    st.markdown(f"**総論文数**: {len(papers)} 件")

    st.markdown("---")

    # フィルタセクション
    st.subheader("🔍 フィルタ・検索")

    col_filter1, col_filter2, col_filter3 = st.columns(3)

    with col_filter1:
        # 研究タイプフィルタ
        study_types = ["All"] + sorted(set(p.get('study_type', '') for p in papers.values() if p.get('study_type')))
        selected_study_type = st.selectbox("研究タイプ", study_types)

    with col_filter2:
        # Diseaseフィルタ
        diseases = ["All"] + sorted(set(
            p.get('perspectives', {}).get('disease', '')
            for p in papers.values()
            if p.get('perspectives', {}).get('disease') and p.get('perspectives', {}).get('disease') != 'not_applicable'
        ))
        selected_disease = st.selectbox("Disease", diseases)

    with col_filter3:
        # Methodフィルタ
        methods = ["All"] + sorted(set(
            p.get('perspectives', {}).get('method', '')
            for p in papers.values()
            if p.get('perspectives', {}).get('method') and p.get('perspectives', {}).get('method') != 'not_applicable'
        ))
        selected_method = st.selectbox("Method", methods)

    # テキスト検索
    search_term = st.text_input("🔎 キーワード検索", placeholder="タイトル、著者、キーワードで検索...")

    # 年範囲フィルタ
    years = [p.get('year') for p in papers.values() if p.get('year')]
    if years:
        min_year, max_year = min(years), max(years)
        year_range = st.slider("出版年", min_year, max_year, (min_year, max_year))
    else:
        year_range = (1900, 2100)

    st.markdown("---")

    # フィルタリング
    filtered_papers = {}

    for paper_id, paper_data in papers.items():
        # 研究タイプフィルタ
        if selected_study_type != "All" and paper_data.get('study_type') != selected_study_type:
            continue

        # Diseaseフィルタ
        if selected_disease != "All":
            if paper_data.get('perspectives', {}).get('disease') != selected_disease:
                continue

        # Methodフィルタ
        if selected_method != "All":
            if paper_data.get('perspectives', {}).get('method') != selected_method:
                continue

        # 年範囲フィルタ
        paper_year = paper_data.get('year')
        if paper_year and (paper_year < year_range[0] or paper_year > year_range[1]):
            continue

        # テキスト検索
        if search_term:
            search_lower = search_term.lower()
            title = paper_data.get('title', '').lower()
            authors = ' '.join(paper_data.get('authors', [])).lower()
            keywords = ' '.join(paper_data.get('keywords', [])).lower()

            if not (search_lower in title or search_lower in authors or search_lower in keywords):
                continue

        filtered_papers[paper_id] = paper_data

    st.subheader(f"📊 検索結果: {len(filtered_papers)} 件")

    if not filtered_papers:
        st.warning("🔍 条件に一致する論文が見つかりませんでした。")
        st.stop()

    # ソート
    sort_by = st.selectbox(
        "並び替え",
        options=[
            "追加日（新しい順）",
            "追加日（古い順）",
            "年（新しい順）",
            "年（古い順）",
            "タイトル（A-Z）",
            "研究タイプ（A-Z）",
            "Disease（A-Z）",
            "Method（A-Z）",
            "サンプルサイズ（大きい順）",
            "サンプルサイズ（小さい順）"
        ],
        index=0
    )

    # テーブル表示用データ作成
    table_data = []

    for paper_id, paper_data in filtered_papers.items():
        # Obsidianへのリンク
        obsidian_note_path = project_root / "ObsidianVault" / "Papers" / f"{paper_id}.md"
        obsidian_uri = f"obsidian://open?path={obsidian_note_path.absolute()}"

        authors_str = ', '.join(paper_data.get('authors', [])[:3])
        if len(paper_data.get('authors', [])) > 3:
            authors_str += ' et al.'

        table_data.append({
            'ID': paper_id,
            'タイトル': paper_data.get('title', 'N/A')[:80] + ('...' if len(paper_data.get('title', '')) > 80 else ''),
            '著者': authors_str,
            '年': paper_data.get('year', 'N/A'),
            '研究タイプ': paper_data.get('study_type', 'N/A'),
            'Disease': paper_data.get('perspectives', {}).get('disease', '-'),
            'Method': paper_data.get('perspectives', {}).get('method', '-'),
            '優先度': paper_data.get('priority', 'medium'),
            'Obsidianリンク': obsidian_uri,
            '_data': paper_data  # 詳細表示用
        })

    # ソート
    if sort_by == "追加日（新しい順）":
        table_data.sort(key=lambda x: x['_data'].get('date_added', ''), reverse=True)
    elif sort_by == "追加日（古い順）":
        table_data.sort(key=lambda x: x['_data'].get('date_added', ''))
    elif sort_by == "年（新しい順）":
        table_data.sort(key=lambda x: x['_data'].get('year', 0) or 0, reverse=True)
    elif sort_by == "年（古い順）":
        table_data.sort(key=lambda x: x['_data'].get('year', 0) or 0)
    elif sort_by == "タイトル（A-Z）":
        table_data.sort(key=lambda x: x['タイトル'].lower())
    elif sort_by == "研究タイプ（A-Z）":
        table_data.sort(key=lambda x: x['_data'].get('study_type', '').lower())
    elif sort_by == "Disease（A-Z）":
        table_data.sort(key=lambda x: x['_data'].get('perspectives', {}).get('disease', '').lower())
    elif sort_by == "Method（A-Z）":
        table_data.sort(key=lambda x: x['_data'].get('perspectives', {}).get('method', '').lower())
    elif sort_by == "サンプルサイズ（大きい順）":
        def get_sample_size(x):
            size = x['_data'].get('sample_size', 0)
            if isinstance(size, (int, float)):
                return size
            return 0
        table_data.sort(key=get_sample_size, reverse=True)
    elif sort_by == "サンプルサイズ（小さい順）":
        def get_sample_size(x):
            size = x['_data'].get('sample_size', 0)
            if isinstance(size, (int, float)):
                return size
            return float('inf')  # サイズ不明は最後に
        table_data.sort(key=get_sample_size)

    # データフレーム表示（チェックボックス付き）
    display_data = []
    for row in table_data:
        row_data = {k: v for k, v in row.items() if k not in ['Obsidianリンク', '_data']}
        row_data['選択'] = False  # チェックボックス列を先頭に
        display_data.append(row_data)

    df = pd.DataFrame(display_data)

    # 列の順序を変更（選択を先頭に）
    cols = ['選択'] + [col for col in df.columns if col != '選択']
    df = df[cols]

    # 編集可能なデータフレームとして表示
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        height=400,
        column_config={
            "選択": st.column_config.CheckboxColumn(
                "選択",
                help="ダウンロードする論文を選択",
                default=False,
            )
        },
        disabled=[col for col in df.columns if col != '選択']  # 選択列以外は編集不可
    )

    # 選択された論文のIDリスト
    selected_paper_ids = [
        table_data[i]['ID']
        for i in range(len(edited_df))
        if edited_df.iloc[i]['選択']
    ]

    # ダウンロードボタン
    if selected_paper_ids:
        st.success(f"✅ {len(selected_paper_ids)} 件の論文が選択されています")

        col_download1, col_download2, col_download3 = st.columns([1, 1, 2])

        with col_download1:
            # ZIPダウンロードボタン
            zip_buffer = create_papers_zip(selected_paper_ids, papers, project_root)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            st.download_button(
                label=f"📦 選択した論文をダウンロード ({len(selected_paper_ids)}件)",
                data=zip_buffer,
                file_name=f"papers_export_{timestamp}.zip",
                mime="application/zip"
            )

        with col_download2:
            # 選択をクリア
            if st.button("🔄 選択をクリア"):
                st.rerun()
    else:
        st.info("💡 ダウンロードしたい論文にチェックを入れてください")

    st.markdown("---")

    # 詳細表示
    st.subheader("📄 論文詳細")

    # 論文選択
    paper_ids = [row['ID'] for row in table_data]
    selected_id = st.selectbox("詳細を見る論文を選択", paper_ids, format_func=lambda x: f"{x} - {next(row['タイトル'] for row in table_data if row['ID'] == x)}")

    if selected_id:
        selected_paper = next(row for row in table_data if row['ID'] == selected_id)
        paper_data = selected_paper['_data']
        obsidian_uri = selected_paper['Obsidianリンク']

        # 詳細情報を表示
        col_detail1, col_detail2 = st.columns([2, 1])

        with col_detail1:
            st.markdown(f"### {paper_data.get('title', 'N/A')}")

            st.markdown(f"""
            **著者**: {', '.join(paper_data.get('authors', ['N/A']))}

            **掲載誌**: {paper_data.get('journal', 'N/A')} ({paper_data.get('year', 'N/A')})

            **巻号ページ**: Vol.{paper_data.get('volume', 'N/A')} No.{paper_data.get('issue', 'N/A')} pp.{paper_data.get('pages', 'N/A')}
            """)

            if paper_data.get('doi'):
                st.markdown(f"**DOI**: [{paper_data['doi']}](https://doi.org/{paper_data['doi']})")

            if paper_data.get('pmid'):
                st.markdown(f"**PMID**: [{paper_data['pmid']}](https://pubmed.ncbi.nlm.nih.gov/{paper_data['pmid']}/)")

        with col_detail2:
            st.markdown("### 🏷️ メタ情報")

            st.markdown(f"""
            **研究タイプ**: {paper_data.get('study_type', 'N/A')}

            **サンプルサイズ**: {paper_data.get('sample_size', 'N/A')}

            **優先度**: {paper_data.get('priority', 'medium')}

            **読了状態**: {paper_data.get('read_status', 'unread')}
            """)

        # Perspectives
        st.markdown("### 📊 Perspectives")

        perspectives = paper_data.get('perspectives', {})
        persp_cols = st.columns(5)

        persp_labels = ['Study Type', 'Disease', 'Method', 'Analysis', 'Population']
        persp_keys = ['study_type', 'disease', 'method', 'analysis', 'population']

        for col, label, key in zip(persp_cols, persp_labels, persp_keys):
            value = perspectives.get(key, 'N/A')
            if value and value != 'not_applicable':
                col.metric(label, value)
            else:
                col.metric(label, '-')

        # Abstract
        if paper_data.get('abstract'):
            st.markdown("### 📄 Abstract")
            with st.expander("クリックで表示"):
                st.write(paper_data['abstract'])

        # Summary
        if paper_data.get('summary'):
            st.markdown("### 📝 要約")
            st.write(paper_data['summary'])

        # Keywords
        if paper_data.get('keywords'):
            st.markdown("### 🏷️ Keywords")
            st.write(', '.join([f"`{kw}`" for kw in paper_data['keywords']]))

        # Obsidianで開くボタン
        st.markdown("---")

        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)

        with col_btn1:
            st.markdown(f"""
            <a href="{obsidian_uri}" target="_blank" style="
                display: inline-block;
                background-color: #7c3aed;
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 0.3rem;
                text-decoration: none;
                text-align: center;
                width: 100%;
            ">
                📖 Obsidianで開く
            </a>
            """, unsafe_allow_html=True)

        with col_btn2:
            pdf_path = paper_data.get('pdf_path')
            if pdf_path and Path(pdf_path).exists():
                st.markdown(f"""
                <a href="file:///{pdf_path}" target="_blank" style="
                    display: inline-block;
                    background-color: #ef4444;
                    color: white;
                    padding: 0.5rem 1rem;
                    border-radius: 0.3rem;
                    text-decoration: none;
                    text-align: center;
                    width: 100%;
                ">
                    📄 PDFを開く
                </a>
                """, unsafe_allow_html=True)

        with col_btn3:
            # 個別ダウンロードボタン
            pdf_path = paper_data.get('pdf_path')
            if pdf_path and Path(pdf_path).exists():
                with open(pdf_path, 'rb') as f:
                    pdf_data = f.read()
                    pdf_filename = Path(pdf_path).name

                st.download_button(
                    label="💾 PDFをダウンロード",
                    data=pdf_data,
                    file_name=pdf_filename,
                    mime="application/pdf",
                    use_container_width=True
                )

        with col_btn4:
            # MOCへのリンク
            disease_tag = perspectives.get('disease')
            if disease_tag and disease_tag != 'not_applicable':
                moc_path = project_root / "ObsidianVault" / "MOC" / f"{disease_tag}_view.md"
                moc_uri = f"obsidian://open?path={moc_path.absolute()}"

                st.markdown(f"""
                <a href="{moc_uri}" target="_blank" style="
                    display: inline-block;
                    background-color: #10b981;
                    color: white;
                    padding: 0.5rem 1rem;
                    border-radius: 0.3rem;
                    text-decoration: none;
                    text-align: center;
                    width: 100%;
                ">
                    🗂️ MOCを開く
                </a>
                """, unsafe_allow_html=True)

except FileNotFoundError:
    st.error("📭 カタログファイルが見つかりません。論文を追加してください。")
except Exception as e:
    st.error(f"❌ エラーが発生しました: {e}")
    import traceback
    st.code(traceback.format_exc())
