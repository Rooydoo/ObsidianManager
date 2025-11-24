"""
ネットワーク可視化ページ
タグベースの論文関係を可視化
"""

import streamlit as st
import sys
from pathlib import Path
import json
import plotly.graph_objects as go
import networkx as nx
from collections import defaultdict

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# ページ設定
st.set_page_config(page_title="ネットワーク可視化", page_icon="🔗", layout="wide")

# データ読み込み
@st.cache_data
def load_catalog():
    """カタログデータを読み込み"""
    catalog_path = project_root / "data" / "catalog.json"
    with open(catalog_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_paper_network(papers, group_by='disease', min_connections=1):
    """
    論文ネットワークグラフを作成

    Args:
        papers: 論文データ
        group_by: グルーピング軸 ('disease', 'method', 'study_type')
        min_connections: 最小エッジ数（これ以下は表示しない）

    Returns:
        NetworkX Graph
    """
    G = nx.Graph()

    # タググループごとに論文を分類
    tag_to_papers = defaultdict(list)

    for paper_id, paper_data in papers.items():
        # グルーピング軸に応じてタグを取得
        if group_by == 'study_type':
            tag = paper_data.get('study_type', 'unknown')
        else:
            tag = paper_data.get('perspectives', {}).get(group_by, 'unknown')

        if tag and tag != 'not_applicable' and tag != 'unknown':
            tag_to_papers[tag].append(paper_id)

            # ノードを追加
            if not G.has_node(paper_id):
                G.add_node(
                    paper_id,
                    title=paper_data.get('title', 'N/A')[:50] + '...',
                    full_title=paper_data.get('title', 'N/A'),
                    year=paper_data.get('year', 'N/A'),
                    group=tag,
                    authors=', '.join(paper_data.get('authors', [])[:2]),
                    study_type=paper_data.get('study_type', 'N/A')
                )

    # 同じタググループ内の論文同士をエッジで繋ぐ
    for tag, paper_list in tag_to_papers.items():
        for i, paper_id1 in enumerate(paper_list):
            for paper_id2 in paper_list[i+1:]:
                if G.has_node(paper_id1) and G.has_node(paper_id2):
                    # 既にエッジがあれば重みを増やす
                    if G.has_edge(paper_id1, paper_id2):
                        G[paper_id1][paper_id2]['weight'] += 1
                    else:
                        G.add_edge(paper_id1, paper_id2, weight=1, tag=tag)

    # 最小エッジ数以下のノードを削除
    nodes_to_remove = [node for node in G.nodes() if G.degree(node) < min_connections]
    G.remove_nodes_from(nodes_to_remove)

    return G

def create_plotly_network(G, group_by='disease'):
    """
    Plotlyでインタラクティブなネットワークグラフを作成
    """
    # レイアウト計算
    pos = nx.spring_layout(G, k=2, iterations=50)

    # エッジのトレース
    edge_trace = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        weight = G[edge[0]][edge[1]].get('weight', 1)

        edge_trace.append(
            go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=weight * 0.5, color='rgba(125, 125, 125, 0.3)'),
                hoverinfo='none',
                showlegend=False
            )
        )

    # ノードのグループ分け（色分け用）
    groups = defaultdict(list)
    for node in G.nodes():
        group = G.nodes[node]['group']
        groups[group].append(node)

    # カラーパレット
    colors = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]

    # グループごとにノードトレースを作成
    node_traces = []
    for i, (group, nodes) in enumerate(groups.items()):
        node_x = []
        node_y = []
        node_text = []

        for node in nodes:
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            node_info = G.nodes[node]
            hover_text = (
                f"<b>{node_info['full_title']}</b><br>"
                f"Authors: {node_info['authors']}<br>"
                f"Year: {node_info['year']}<br>"
                f"Type: {node_info['study_type']}<br>"
                f"{group_by.capitalize()}: {group}"
            )
            node_text.append(hover_text)

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers',
            name=group,
            hovertemplate='%{text}<extra></extra>',
            text=node_text,
            marker=dict(
                size=15,
                color=colors[i % len(colors)],
                line=dict(width=2, color='white')
            )
        )
        node_traces.append(node_trace)

    # 図を作成
    fig = go.Figure(data=edge_trace + node_traces)

    fig.update_layout(
        title=f"論文ネットワーク（{group_by} でグルーピング）",
        titlefont_size=16,
        showlegend=True,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=700,
        plot_bgcolor='rgba(240,240,240,0.9)'
    )

    return fig

# タイトル
st.title("🔗 論文ネットワーク可視化")

st.markdown("""
論文をタグでグルーピングし、ネットワークグラフとして可視化します。
同じタググループに属する論文同士が線で繋がれています。
""")

try:
    catalog = load_catalog()
    papers = catalog['papers']

    if not papers:
        st.info("📭 まだ論文が登録されていません。「📄 Add Paper」から追加してください。")
        st.stop()

    st.markdown("---")

    # コントロールパネル
    st.subheader("⚙️ 表示設定")

    col1, col2, col3 = st.columns(3)

    with col1:
        group_by = st.selectbox(
            "グルーピング軸",
            options=['disease', 'method', 'study_type'],
            format_func=lambda x: {
                'disease': '疾患（Disease）',
                'method': '手法（Method）',
                'study_type': '研究タイプ'
            }[x]
        )

    with col2:
        min_connections = st.slider(
            "最小接続数",
            min_value=0,
            max_value=5,
            value=1,
            help="この数以下の接続しか持たない論文は表示されません"
        )

    with col3:
        st.metric("総論文数", len(papers))

    st.markdown("---")

    # ネットワークグラフ生成
    with st.spinner('ネットワークを計算中...'):
        G = create_paper_network(papers, group_by=group_by, min_connections=min_connections)

        if len(G.nodes()) == 0:
            st.warning("⚠️ 表示する論文がありません。最小接続数を下げるか、論文を追加してください。")
            st.stop()

        st.success(f"✅ {len(G.nodes())} 件の論文、{len(G.edges())} 本の接続を表示")

        fig = create_plotly_network(G, group_by=group_by)
        st.plotly_chart(fig, use_container_width=True)

    # 統計情報
    st.markdown("---")
    st.subheader("📊 ネットワーク統計")

    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

    with col_stat1:
        st.metric("ノード数", len(G.nodes()))

    with col_stat2:
        st.metric("エッジ数", len(G.edges()))

    with col_stat3:
        density = nx.density(G)
        st.metric("密度", f"{density:.3f}")

    with col_stat4:
        if len(G.nodes()) > 0:
            avg_degree = sum(dict(G.degree()).values()) / len(G.nodes())
            st.metric("平均次数", f"{avg_degree:.2f}")

    # グループ別統計
    st.markdown("---")
    st.subheader(f"🏷️ {group_by.capitalize()} 別の論文数")

    group_counts = defaultdict(int)
    for node in G.nodes():
        group = G.nodes[node]['group']
        group_counts[group] += 1

    group_data = sorted(group_counts.items(), key=lambda x: x[1], reverse=True)

    col_group1, col_group2 = st.columns(2)

    with col_group1:
        for tag, count in group_data[:len(group_data)//2]:
            st.write(f"**{tag}**: {count} 件")

    with col_group2:
        for tag, count in group_data[len(group_data)//2:]:
            st.write(f"**{tag}**: {count} 件")

    # Obsidianリンク
    st.markdown("---")
    st.info("💡 より詳細な分析は、Obsidianのグラフビューで行えます。")

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
