#!/usr/bin/env python3
"""
論文からQ&Aペアを自動生成するスクリプト
Claude APIを使用して医学論文を分析し、重要な情報をQ&A形式で抽出
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
import anthropic

# プロジェクトルート
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.pdf_processor import PDFProcessor


class QAGenerator:
    """Q&A自動生成クラス"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初期化

        Args:
            api_key: Claude API key（Noneの場合は環境変数から取得）
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.pdf_processor = PDFProcessor()

        # プロンプトテンプレートを読み込み
        prompt_path = project_root / "scripts" / "prompts" / "qa_generation_prompt.txt"
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.prompt_template = f.read()

    def generate_qa_from_pdf(
        self,
        pdf_path: Path,
        paper_metadata: Dict,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096
    ) -> List[Dict]:
        """
        PDFからQ&Aペアを生成

        Args:
            pdf_path: PDFファイルのパス
            paper_metadata: 論文のメタデータ
            model: 使用するClaudeモデル
            max_tokens: 最大トークン数

        Returns:
            Q&Aペアのリスト
        """
        # PDFから全文テキストを抽出
        print(f"📄 PDFからテキストを抽出中: {pdf_path.name}")
        full_text = self.pdf_processor.extract_text(pdf_path, max_pages=0)

        if not full_text or len(full_text) < 500:
            raise ValueError("PDFから十分なテキストを抽出できませんでした")

        # プロンプトを構築
        prompt = self.prompt_template.format(
            title=paper_metadata.get('title', 'N/A'),
            authors=', '.join(paper_metadata.get('authors', [])),
            journal=paper_metadata.get('journal', 'N/A'),
            year=paper_metadata.get('year', 'N/A'),
            full_text=full_text[:50000]  # トークン制限のため最初の50000文字
        )

        print("🤖 Claude APIでQ&Aを生成中...")

        # Claude APIを呼び出し
        try:
            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # レスポンスからJSONを抽出
            response_text = message.content[0].text

            # JSON部分を抽出（```json と ``` で囲まれている場合に対応）
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.rfind("```")
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.rfind("```")
                response_text = response_text[json_start:json_end].strip()

            # JSONをパース
            qa_data = json.loads(response_text)
            qa_pairs = qa_data.get('qa_pairs', [])

            print(f"✅ {len(qa_pairs)} 個のQ&Aペアを生成しました")
            return qa_pairs

        except Exception as e:
            print(f"❌ エラー: Q&A生成に失敗しました: {e}")
            raise

    def save_qa_to_catalog(
        self,
        paper_id: str,
        qa_pairs: List[Dict]
    ):
        """
        生成したQ&AをCatalogに保存

        Args:
            paper_id: 論文ID
            qa_pairs: Q&Aペアのリスト
        """
        catalog_path = project_root / "data" / "catalog.json"

        # Catalogを読み込み
        with open(catalog_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)

        # Q&Aを追加
        if paper_id in catalog['papers']:
            catalog['papers'][paper_id]['qa_pairs'] = qa_pairs
            catalog['papers'][paper_id]['qa_generated'] = True

            # Catalogを保存
            with open(catalog_path, 'w', encoding='utf-8') as f:
                json.dump(catalog, f, ensure_ascii=False, indent=2)

            print(f"💾 Q&AをCatalogに保存しました: {paper_id}")
        else:
            raise ValueError(f"論文ID {paper_id} がCatalogに見つかりません")


def main():
    """メイン関数"""
    import argparse

    parser = argparse.ArgumentParser(description='論文からQ&Aペアを自動生成')
    parser.add_argument('paper_id', help='論文ID (例: paper001)')
    parser.add_argument('--api-key', help='Claude API key（省略時は環境変数から取得）')
    parser.add_argument('--model', default='claude-3-5-sonnet-20241022', help='使用するClaudeモデル')

    args = parser.parse_args()

    # Catalogを読み込み
    catalog_path = project_root / "data" / "catalog.json"
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    # 論文メタデータを取得
    if args.paper_id not in catalog['papers']:
        print(f"❌ エラー: 論文ID {args.paper_id} が見つかりません")
        sys.exit(1)

    paper_data = catalog['papers'][args.paper_id]
    pdf_path = Path(paper_data['pdf_path'])

    if not pdf_path.exists():
        print(f"❌ エラー: PDFファイルが見つかりません: {pdf_path}")
        sys.exit(1)

    # Q&A生成
    generator = QAGenerator(api_key=args.api_key)

    try:
        qa_pairs = generator.generate_qa_from_pdf(
            pdf_path=pdf_path,
            paper_metadata=paper_data,
            model=args.model
        )

        # Catalogに保存
        generator.save_qa_to_catalog(args.paper_id, qa_pairs)

        print("\n✅ Q&A生成が完了しました！")
        print(f"生成されたQ&A数: {len(qa_pairs)}")

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
