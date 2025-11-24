"""
階層的可視化ページ
メタタグの多階層グルーピングをサンキーダイアグラムで可視化
"""

import streamlit as st
import sys
from pathlib import Path
import json
import plotly.graph_objects as go
from collections import defaultdict, Counter

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# ページ設定
st.set_page_config(page_title="階層的可視化", page_icon="📊", layout="wide")

# データ読み込み
@st.cache_data
def load_catalog():
    """カタログデータを読み込み"""
    catalog_path = project_root / "data" / "catalog.json"
    with open(catalog_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_tag_value(paper_data, meta_tag):
    """
    論文データから指定されたメタタグの値を取得

    Args:
        paper_data: 論文データ
        meta_tag: メタタグ名 (study_type, disease, method, analysis, population)

    Returns:
        タグ値（文字列）
    """
    if meta_tag == 'study_type':
        value = paper_data.get('study_type', 'unknown')
    else:
        value = paper_data.get('perspectives', {}).get(meta_tag, 'unknown')

    # 空や無効な値を処理
    if not value or value == 'not_applicable':
        return 'other'

    return value

def create_hierarchical_data(papers, hierarchy_levels):
    """
    階層的データ構造を作成

    Args:
        papers: 論文データ
        hierarchy_levels: 階層のリスト ['study_type', 'disease', 'method']

    Returns:
        論文を階層的にグルーピングしたデータ
    """
    # 階層ごとに論文を分類
    hierarchical_groups = defaultdict(lambda: defaultdict(list))

    for paper_id, paper_data in papers.items():
        # 各階層のパスを構築
        path = []
        for level in hierarchy_levels:
            tag_value = get_tag_value(paper_data, level)
            path.append(tag_value)

        # パスに従って論文を格納
        current_key = tuple(path)
        hierarchical_groups[len(path)][current_key].append({
            'id': paper_id,
            'title': paper_data.get('title', 'N/A'),
            'year': paper_data.get('year', 'N/A')
        })

    return hierarchical_groups

def create_sankey_diagram(papers, hierarchy_levels):
    """
    サンキーダイアグラムを作成

    Args:
        papers: 論文データ
        hierarchy_levels: 階層のリスト

    Returns:
        Plotly Figure
    """
    # ノードとリンクのデータ構造
    nodes = []
    node_indices = {}
    links = {
        'source': [],
        'target': [],
        'value': [],
        'customdata': []
    }

    # 各論文の階層パスを取得
    paper_paths = []
    for paper_id, paper_data in papers.items():
        path = []
        for level in hierarchy_levels:
            tag_value = get_tag_value(paper_data, level)
            path.append(tag_value)
        paper_paths.append(path)

    # 各階層のノードを作成
    for level_idx, level_name in enumerate(hierarchy_levels):
        # この階層の全タグを収集
        tags_at_level = set(path[level_idx] for path in paper_paths)

        for tag in sorted(tags_at_level):
            node_label = f"{tag}"
            node_full_name = f"{level_name}:{tag}"

            if node_full_name not in node_indices:
                node_indices[node_full_name] = len(nodes)
                nodes.append(node_label)

    # リンクを作成（階層間の接続）
    for level_idx in range(len(hierarchy_levels) - 1):
        # この階層から次の階層へのフローをカウント
        flows = Counter()

        for path in paper_paths:
            source_tag = path[level_idx]
            target_tag = path[level_idx + 1]

            source_node = f"{hierarchy_levels[level_idx]}:{source_tag}"
            target_node = f"{hierarchy_levels[level_idx + 1]}:{target_tag}"

            flows[(source_node, target_node)] += 1

        # フローをリンクに変換
        for (source, target), count in flows.items():
            if source in node_indices and target in node_indices:
                links['source'].append(node_indices[source])
                links['target'].append(node_indices[target])
                links['value'].append(count)
                links['customdata'].append(f"{count} papers")

    # サンキーダイアグラムを作成
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=nodes,
            color="lightblue"
        ),
        link=dict(
            source=links['source'],
            target=links['target'],
            value=links['value'],
            customdata=links['customdata'],
            hovertemplate='%{customdata}<extra></extra>'
        )
    )])

    hierarchy_str = ' → '.join(hierarchy_levels)
    fig.update_layout(
        title=f"論文の階層的フロー: {hierarchy_str}",
        font=dict(size=12),
        height=600
    )

    return fig

def create_sunburst_diagram(papers, hierarchy_levels):
    """
    サンバーストチャートを作成

    Args:
        papers: 論文データ
        hierarchy_levels: 階層のリスト

    Returns:
        Plotly Figure
    """
    # データを階層構造に変換
    labels = []
    parents = []
    values = []

    # ルートノード
    labels.append("All Papers")
    parents.append("")
    values.append(len(papers))

    # 各論文の階層パスを取得
    paper_paths = []
    for paper_id, paper_data in papers.items():
        path = []
        for level in hierarchy_levels:
            tag_value = get_tag_value(paper_data, level)
            path.append(tag_value)
        paper_paths.append(path)

    # 階層ごとにノードを構築
    path_counts = Counter(tuple(path[:i+1]) for path in paper_paths for i in range(len(path)))

    for path, count in path_counts.items():
        # パスから親を決定
        if len(path) == 1:
            parent = "All Papers"
        else:
            parent_path = path[:-1]
            parent = " - ".join(parent_path)

        node_label = " - ".join(path)
        labels.append(node_label)
        parents.append(parent)
        values.append(count)

    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        hovertemplate='<b>%{label}</b><br>Papers: %{value}<extra></extra>'
    ))

    hierarchy_str = ' → '.join(hierarchy_levels)
    fig.update_layout(
        title=f"論文の階層構造: {hierarchy_str}",
        height=700
    )

    return fig

# タイトル
st.title("📊 階層的可視化")

st.markdown("""
メタタグを自由に組み合わせて、論文を多階層的に可視化します。
階層の数と各階層で使用するメタタグを選択できます。
""")

try:
    catalog = load_catalog()
    papers = catalog['papers']

    if not papers:
        st.info("📭 まだ論文が登録されていません。「📄 Add Paper」から追加してください。")
        st.stop()

    st.markdown("---")

    # コントロールパネル
    st.subheader("⚙️ 階層設定")

    # 利用可能なメタタグ
    available_tags = {
        'study_type': '研究タイプ',
        'disease': '疾患',
        'method': '手法',
        'analysis': '解析手法',
        'population': '対象集団'
    }

    col1, col2 = st.columns([1, 3])

    with col1:
        num_levels = st.selectbox(
            "階層の数",
            options=[2, 3, 4, 5],
            index=1,  # デフォルトは3階層
            help="表示する階層の数を選択"
        )

    with col2:
        st.info(f"💡 {num_levels}つのメタタグを選択してください（重複なし）")

    # 階層ごとのメタタグ選択
    st.markdown("### 各階層のメタタグ選択")

    hierarchy_levels = []
    used_tags = set()

    cols = st.columns(num_levels)

    for i in range(num_levels):
        with cols[i]:
            # 使用済みタグを除外
            available_options = {k: v for k, v in available_tags.items() if k not in used_tags}

            if not available_options:
                st.warning(f"階層{i+1}: タグが不足")
                continue

            selected_tag = st.selectbox(
                f"階層 {i+1}",
                options=list(available_options.keys()),
                format_func=lambda x: available_options[x],
                key=f"level_{i}"
            )

            hierarchy_levels.append(selected_tag)
            used_tags.add(selected_tag)

    # 可視化タイプ選択
    st.markdown("---")
    viz_type = st.radio(
        "可視化タイプ",
        options=["サンキーダイアグラム", "サンバーストチャート"],
        horizontal=True
    )

    st.markdown("---")

    # 可視化実行
    if len(hierarchy_levels) == num_levels:
        with st.spinner('可視化を生成中...'):
            if viz_type == "サンキーダイアグラム":
                fig = create_sankey_diagram(papers, hierarchy_levels)
                st.plotly_chart(fig, use_container_width=True)
            else:
                fig = create_sunburst_diagram(papers, hierarchy_levels)
                st.plotly_chart(fig, use_container_width=True)

        # 統計情報
        st.markdown("---")
        st.subheader("📈 階層別統計")

        hierarchy_data = create_hierarchical_data(papers, hierarchy_levels)

        # 各階層のユニーク数
        stats_cols = st.columns(num_levels)

        for i, level_name in enumerate(hierarchy_levels):
            with stats_cols[i]:
                # この階層のユニークな値の数
                unique_values = set()
                for paper_id, paper_data in papers.items():
                    value = get_tag_value(paper_data, level_name)
                    unique_values.add(value)

                st.metric(
                    f"{available_tags[level_name]}",
                    f"{len(unique_values)} 種類"
                )

        # 詳細統計
        with st.expander("📊 詳細統計を表示"):
            for level_name in hierarchy_levels:
                st.markdown(f"#### {available_tags[level_name]}")

                # この階層の各値の論文数をカウント
                value_counts = Counter()
                for paper_id, paper_data in papers.items():
                    value = get_tag_value(paper_data, level_name)
                    value_counts[value] += 1

                # ソートして表示
                for value, count in value_counts.most_common():
                    st.write(f"- **{value}**: {count} 件")

                st.markdown("---")

    else:
        st.warning("⚠️ すべての階層にメタタグを選択してください")

    # Obsidianリンク
    st.markdown("---")
    st.info("💡 Obsidianでもタグベースのグラフビューが利用できます。")

    obsidian_vault_path = project_root / "ObsidianVault"
    obsidian_uri = f"obsidian://open?path={obsidian_vault_path.absolute()}"

    st.markdown(f"""
    <a href="{obsidian_uri}" target="_blank" style="
        display: inline-block;
        background-color: #7c3aed;
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        text-decoration: none;
        text-align: center;
        font-weight: bold;
    ">
        📖 Obsidianで開く
    </a>
    """, unsafe_allow_html=True)

except FileNotFoundError:
    st.error("📭 カタログファイルが見つかりません。論文を追加してください。")
except Exception as e:
    st.error(f"❌ エラーが発生しました: {e}")
    import traceback
    st.code(traceback.format_exc())
