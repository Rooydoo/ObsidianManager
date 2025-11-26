#!/usr/bin/env python3
"""
Q&Aペアをベクトル化してChromaDBに保存するスクリプト
"""

import json
import sys
from pathlib import Path
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# プロジェクトルート
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class QAVectorizer:
    """Q&Aベクトル化クラス"""

    def __init__(
        self,
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
        persist_directory: str = None
    ):
        """
        初期化

        Args:
            model_name: 使用する埋め込みモデル
            persist_directory: ChromaDBの永続化ディレクトリ
        """
        print(f"📥 埋め込みモデルをロード中: {model_name}")
        self.model = SentenceTransformer(model_name)

        # ChromaDBクライアントを初期化
        if persist_directory is None:
            persist_directory = str(project_root / "data" / "chroma_db")

        self.persist_directory = persist_directory
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))

        print(f"💾 ChromaDB: {persist_directory}")

    def load_qa_pairs(self) -> List[Dict]:
        """
        catalog.jsonからQ&Aペアを読み込む

        Returns:
            Q&Aペアのリスト（メタデータ付き）
        """
        catalog_path = project_root / "data" / "catalog.json"

        with open(catalog_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)

        all_qa_pairs = []

        for paper_id, paper_data in catalog['papers'].items():
            qa_pairs = paper_data.get('qa_pairs', [])

            if not qa_pairs:
                continue

            for idx, qa in enumerate(qa_pairs):
                # Q&Aペアにメタデータを追加
                qa_with_metadata = {
                    'id': f"{paper_id}_qa_{idx}",
                    'paper_id': paper_id,
                    'question': qa['question'],
                    'answer': qa['answer'],
                    'section': qa.get('section', 'unknown'),
                    'importance': qa.get('importance', 'medium'),
                    'keywords': qa.get('keywords', []),
                    # 論文メタデータも追加
                    'paper_title': paper_data.get('title', 'N/A'),
                    'paper_year': paper_data.get('year', 'N/A'),
                    'study_type': paper_data.get('study_type', 'N/A'),
                    'disease': paper_data.get('perspectives', {}).get('disease', 'N/A'),
                    'method': paper_data.get('perspectives', {}).get('method', 'N/A'),
                }
                all_qa_pairs.append(qa_with_metadata)

        print(f"📊 読み込んだQ&Aペア数: {len(all_qa_pairs)}")
        return all_qa_pairs

    def vectorize_and_store(
        self,
        collection_name: str = "medical_papers_qa"
    ):
        """
        Q&Aペアをベクトル化してChromaDBに保存

        Args:
            collection_name: コレクション名
        """
        # Q&Aペアを読み込み
        qa_pairs = self.load_qa_pairs()

        if not qa_pairs:
            print("⚠️  Q&Aペアが見つかりません。先に generate_qa.py を実行してください。")
            return

        # コレクションを取得または作成
        try:
            # 既存のコレクションを削除
            self.client.delete_collection(name=collection_name)
            print(f"🗑️  既存のコレクション '{collection_name}' を削除しました")
        except:
            pass

        collection = self.client.create_collection(
            name=collection_name,
            metadata={"description": "Medical papers Q&A pairs"}
        )

        print(f"🔄 ベクトル化を開始...")

        # バッチ処理
        batch_size = 100
        for i in range(0, len(qa_pairs), batch_size):
            batch = qa_pairs[i:i+batch_size]

            # 質問と回答を結合してテキスト化
            texts = [
                f"Question: {qa['question']}\nAnswer: {qa['answer']}"
                for qa in batch
            ]

            # 埋め込みベクトルを生成
            embeddings = self.model.encode(texts, convert_to_numpy=True).tolist()

            # メタデータを準備
            metadatas = [
                {
                    'paper_id': qa['paper_id'],
                    'question': qa['question'],
                    'answer': qa['answer'],
                    'section': qa['section'],
                    'importance': qa['importance'],
                    'keywords': json.dumps(qa['keywords'], ensure_ascii=False),
                    'paper_title': qa['paper_title'],
                    'paper_year': str(qa['paper_year']),
                    'study_type': qa['study_type'],
                    'disease': qa['disease'],
                    'method': qa['method'],
                }
                for qa in batch
            ]

            # IDリスト
            ids = [qa['id'] for qa in batch]

            # ChromaDBに保存
            collection.add(
                embeddings=embeddings,
                metadatas=metadatas,
                documents=texts,
                ids=ids
            )

            print(f"  ✅ {i+len(batch)}/{len(qa_pairs)} 件処理完了")

        print(f"\n🎉 ベクトル化完了！")
        print(f"   コレクション名: {collection_name}")
        print(f"   総Q&A数: {len(qa_pairs)}")
        print(f"   保存先: {self.persist_directory}")

    def search(
        self,
        query: str,
        n_results: int = 5,
        collection_name: str = "medical_papers_qa",
        filter_metadata: Dict = None
    ) -> List[Dict]:
        """
        セマンティック検索

        Args:
            query: 検索クエリ
            n_results: 返す結果数
            collection_name: コレクション名
            filter_metadata: フィルタ条件（例: {"disease": "stroke"}）

        Returns:
            検索結果のリスト
        """
        collection = self.client.get_collection(name=collection_name)

        # クエリをベクトル化
        query_embedding = self.model.encode([query], convert_to_numpy=True).tolist()

        # 検索実行
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where=filter_metadata
        )

        # 結果を整形
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'distance': results['distances'][0][i],
                'metadata': results['metadatas'][0][i],
                'document': results['documents'][0][i]
            })

        return formatted_results


def main():
    """メイン関数"""
    import argparse

    parser = argparse.ArgumentParser(description='Q&Aペアをベクトル化')
    parser.add_argument(
        '--model',
        default='paraphrase-multilingual-MiniLM-L12-v2',
        help='埋め込みモデル名'
    )
    parser.add_argument(
        '--collection',
        default='medical_papers_qa',
        help='コレクション名'
    )

    args = parser.parse_args()

    # ベクトル化実行
    vectorizer = QAVectorizer(model_name=args.model)
    vectorizer.vectorize_and_store(collection_name=args.collection)

    print("\n✅ 完了しました！")
    print("   次のステップ: Streamlit UIでセマンティック検索を使用できます")


if __name__ == '__main__':
    main()
