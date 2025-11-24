"""
統計ダッシュボード
"""

import streamlit as st
import sys
from pathlib import Path
import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from collections import Counter

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# ページ設定
st.set_page_config(page_title="統計", page_icon="📊", layout="wide")

# データ読み込み
@st.cache_data
def load_catalog():
    """カタログデータを読み込み"""
    catalog_path = project_root / "data" / "catalog.json"
    with open(catalog_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# タイトル
st.title("📊 統計ダッシュボード")

try:
    catalog = load_catalog()
    papers = catalog['papers']
    metadata = catalog['metadata']

    if not papers:
        st.info("📭 まだ論文が登録されていません。")
        st.stop()

    # サマリーメトリクス
    st.subheader("📈 サマリー")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("総論文数", metadata.get('total_papers', 0))

    with col2:
        # 最多の研究タイプ
        study_types = metadata.get('study_type_distribution', {})
        if study_types:
            top_type = max(study_types, key=study_types.get)
            st.metric("最多研究タイプ", top_type, f"{study_types[top_type]}件")
        else:
            st.metric("最多研究タイプ", "N/A")

    with col3:
        # 最多のDisease
        diseases = metadata.get('disease_distribution', {})
        if diseases:
            top_disease = max(diseases, key=diseases.get)
            st.metric("最多Disease", top_disease, f"{diseases[top_disease]}件")
        else:
            st.metric("最多Disease", "N/A")

    with col4:
        # 最新の論文
        sorted_papers = sorted(
            papers.items(),
            key=lambda x: x[1].get('date_added', ''),
            reverse=True
        )
        if sorted_papers:
            latest_id = sorted_papers[0][0]
            st.metric("最新論文", latest_id)
        else:
            st.metric("最新論文", "N/A")

    st.markdown("---")

    # グラフ表示
    tab1, tab2, tab3, tab4 = st.tabs(["研究タイプ", "年代分布", "Perspectives", "タグ分析"])

    with tab1:
        st.subheader("🔬 研究タイプ分布")

        col_pie, col_bar = st.columns(2)

        with col_pie:
            # 円グラフ
            study_type_dist = metadata.get('study_type_distribution', {})
            if study_type_dist:
                fig_pie = px.pie(
                    values=list(study_type_dist.values()),
                    names=list(study_type_dist.keys()),
                    title="研究タイプ別割合"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("データがありません")

        with col_bar:
            # 棒グラフ
            if study_type_dist:
                fig_bar = px.bar(
                    x=list(study_type_dist.keys()),
                    y=list(study_type_dist.values()),
                    title="研究タイプ別論文数",
                    labels={'x': '研究タイプ', 'y': '論文数'}
                )
                st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        st.subheader("📅 年代別分布")

        # 年代別データ作成
        years = [p.get('year') for p in papers.values() if p.get('year')]

        if years:
            year_counts = Counter(years)

            # ヒストグラム
            fig_hist = px.histogram(
                x=years,
                nbins=len(set(years)),
                title="出版年の分布",
                labels={'x': '年', 'y': '論文数'}
            )
            st.plotly_chart(fig_hist, use_container_width=True)

            # 累積グラフ
            sorted_years = sorted(year_counts.items())
            cumulative = []
            total = 0
            for year, count in sorted_years:
                total += count
                cumulative.append((year, total))

            fig_cumulative = go.Figure()
            fig_cumulative.add_trace(go.Scatter(
                x=[y[0] for y in cumulative],
                y=[y[1] for y in cumulative],
                mode='lines+markers',
                name='累積論文数'
            ))
            fig_cumulative.update_layout(
                title="累積論文数の推移",
                xaxis_title="年",
                yaxis_title="累積論文数"
            )
            st.plotly_chart(fig_cumulative, use_container_width=True)

        else:
            st.info("年データがありません")

    with tab3:
        st.subheader("🎯 Perspectives分布")

        # 各perspectiveの分布
        col_persp1, col_persp2 = st.columns(2)

        with col_persp1:
            # Disease分布
            disease_dist = metadata.get('disease_distribution', {})
            if disease_dist:
                fig_disease = px.bar(
                    x=list(disease_dist.keys()),
                    y=list(disease_dist.values()),
                    title="Disease分布",
                    labels={'x': 'Disease', 'y': '論文数'}
                )
                st.plotly_chart(fig_disease, use_container_width=True)

            # Method分布
            method_dist = metadata.get('method_distribution', {})
            if method_dist:
                fig_method = px.bar(
                    x=list(method_dist.keys()),
                    y=list(method_dist.values()),
                    title="Method分布",
                    labels={'x': 'Method', 'y': '論文数'}
                )
                st.plotly_chart(fig_method, use_container_width=True)

        with col_persp2:
            # Analysis分布
            analysis_dist = metadata.get('analysis_distribution', {})
            if analysis_dist:
                fig_analysis = px.bar(
                    x=list(analysis_dist.keys()),
                    y=list(analysis_dist.values()),
                    title="Analysis分布",
                    labels={'x': 'Analysis', 'y': '論文数'}
                )
                st.plotly_chart(fig_analysis, use_container_width=True)

            # Population分布
            population_dist = metadata.get('population_distribution', {})
            if population_dist:
                fig_population = px.bar(
                    x=list(population_dist.keys()),
                    y=list(population_dist.values()),
                    title="Population分布",
                    labels={'x': 'Population', 'y': '論文数'}
                )
                st.plotly_chart(fig_population, use_container_width=True)

    with tab4:
        st.subheader("🏷️ タグ分析")

        # キーワード頻度
        all_keywords = []
        for paper in papers.values():
            all_keywords.extend(paper.get('keywords', []))

        if all_keywords:
            keyword_counts = Counter(all_keywords)
            top_keywords = keyword_counts.most_common(20)

            # ワードクラウド風の棒グラフ
            fig_keywords = px.bar(
                x=[k[0] for k in top_keywords],
                y=[k[1] for k in top_keywords],
                title="頻出キーワード Top 20",
                labels={'x': 'キーワード', 'y': '出現回数'}
            )
            st.plotly_chart(fig_keywords, use_container_width=True)

            # テーブル表示
            st.markdown("### キーワード一覧")
            keyword_df = pd.DataFrame(top_keywords, columns=['キーワード', '出現回数'])
            st.dataframe(keyword_df, use_container_width=True, hide_index=True)

        else:
            st.info("キーワードデータがありません")

        # タグ共起分析
        st.markdown("### タグ共起パターン")

        # Disease x Method のクロス集計
        cross_data = []
        for paper in papers.values():
            perspectives = paper.get('perspectives', {})
            disease = perspectives.get('disease', '')
            method = perspectives.get('method', '')

            if disease and disease != 'not_applicable' and method and method != 'not_applicable':
                cross_data.append((disease, method))

        if cross_data:
            cross_counter = Counter(cross_data)
            cross_df = pd.DataFrame(
                [(d, m, count) for (d, m), count in cross_counter.most_common(10)],
                columns=['Disease', 'Method', '共起回数']
            )

            st.dataframe(cross_df, use_container_width=True, hide_index=True)

            # ヒートマップ（上位のみ）
            if len(cross_data) > 5:
                # Disease x Method のマトリックス作成
                diseases_list = sorted(set(d for d, m in cross_data))[:10]
                methods_list = sorted(set(m for d, m in cross_data))[:10]

                matrix = [[0 for _ in methods_list] for _ in diseases_list]

                for (d, m), count in cross_counter.items():
                    if d in diseases_list and m in methods_list:
                        i = diseases_list.index(d)
                        j = methods_list.index(m)
                        matrix[i][j] = count

                fig_heatmap = go.Figure(data=go.Heatmap(
                    z=matrix,
                    x=methods_list,
                    y=diseases_list,
                    colorscale='Blues'
                ))
                fig_heatmap.update_layout(
                    title="Disease x Method 共起ヒートマップ",
                    xaxis_title="Method",
                    yaxis_title="Disease"
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)

        else:
            st.info("共起データがありません")

    st.markdown("---")

    # 詳細統計
    st.subheader("📋 詳細統計")

    # サンプルサイズの分布
    sample_sizes = [p.get('sample_size') for p in papers.values() if p.get('sample_size')]

    if sample_sizes:
        col_stats1, col_stats2 = st.columns(2)

        with col_stats1:
            st.markdown("### サンプルサイズ統計")
            st.write(f"**平均**: {sum(sample_sizes) / len(sample_sizes):.1f}")
            st.write(f"**中央値**: {sorted(sample_sizes)[len(sample_sizes)//2]}")
            st.write(f"**最小**: {min(sample_sizes)}")
            st.write(f"**最大**: {max(sample_sizes)}")

        with col_stats2:
            # ヒストグラム
            fig_sample = px.histogram(
                x=sample_sizes,
                nbins=20,
                title="サンプルサイズの分布",
                labels={'x': 'サンプルサイズ', 'y': '論文数'}
            )
            st.plotly_chart(fig_sample, use_container_width=True)

    # ジャーナル分布
    journals = [p.get('journal') for p in papers.values() if p.get('journal')]

    if journals:
        journal_counts = Counter(journals)
        top_journals = journal_counts.most_common(10)

        st.markdown("### 掲載ジャーナル Top 10")

        journal_df = pd.DataFrame(top_journals, columns=['ジャーナル', '論文数'])
        st.dataframe(journal_df, use_container_width=True, hide_index=True)

except FileNotFoundError:
    st.error("📭 カタログファイルが見つかりません。")
except Exception as e:
    st.error(f"❌ エラーが発生しました: {e}")
    import traceback
    st.code(traceback.format_exc())
