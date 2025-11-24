#!/usr/bin/env python3
"""
論文エクスポートスクリプト

選択された論文をプロジェクトフォルダにエクスポート
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set
import logging
import re

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils import PDFProcessor, GitManager

# ロガー設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PaperExporter:
    """論文エクスポートクラス"""

    def __init__(self):
        self.project_root = project_root
        self.catalog_path = project_root / "data" / "catalog.json"
        self.vault_dir = project_root / "ObsidianVault"

        # カタログ読み込み
        with open(self.catalog_path, 'r', encoding='utf-8') as f:
            self.catalog = json.load(f)

        self.pdf_processor = PDFProcessor()

    def export_from_selection_note(self, selection_note_path: Path,
                                   export_dir: Path,
                                   extract_full_text: bool = True,
                                   create_rag_index: bool = True):
        """
        選択ノートから論文をエクスポート

        Args:
            selection_note_path: 選択ノートのパス（チェックボックス付きリンク）
            export_dir: エクスポート先ディレクトリ
            extract_full_text: 全文テキスト抽出するか
            create_rag_index: RAGインデックスを作成するか
        """
        print("\n" + "="*60)
        print("論文エクスポート")
        print("="*60 + "\n")

        # 選択ノートから論文IDを抽出
        paper_ids = self._parse_selection_note(selection_note_path)

        if not paper_ids:
            print("選択された論文がありません")
            return

        print(f"選択された論文: {len(paper_ids)} 件\n")

        # エクスポート実行
        self._export_papers(
            paper_ids,
            export_dir,
            extract_full_text,
            create_rag_index
        )

        print("\n" + "="*60)
        print(f"✓ エクスポート完了: {export_dir}")
        print("="*60 + "\n")

    def _parse_selection_note(self, note_path: Path) -> List[str]:
        """
        選択ノートからチェックされた論文IDを抽出

        Args:
            note_path: 選択ノートのパス

        Returns:
            論文IDのリスト
        """
        if not note_path.exists():
            logger.error(f"Selection note not found: {note_path}")
            return []

        paper_ids = []

        with open(note_path, 'r', encoding='utf-8') as f:
            for line in f:
                # チェックされた項目: - [x] [[paper001]]
                if re.match(r'^\s*-\s*\[x\]\s*\[\[(.+?)\]\]', line, re.IGNORECASE):
                    match = re.search(r'\[\[(.+?)\]\]', line)
                    if match:
                        link = match.group(1)
                        # paper001 形式の場合
                        if link.startswith('paper'):
                            paper_ids.append(link)

        logger.info(f"Found {len(paper_ids)} selected papers")
        return paper_ids

    def _export_papers(self, paper_ids: List[str], export_dir: Path,
                      extract_full_text: bool, create_rag_index: bool):
        """
        論文をエクスポート

        Args:
            paper_ids: エクスポートする論文IDのリスト
            export_dir: エクスポート先
            extract_full_text: 全文抽出するか
            create_rag_index: RAGインデックス作成するか
        """
        # ディレクトリ作成
        export_dir.mkdir(parents=True, exist_ok=True)
        (export_dir / "pdfs").mkdir(exist_ok=True)
        (export_dir / "metadata").mkdir(exist_ok=True)

        if extract_full_text:
            (export_dir / "texts").mkdir(exist_ok=True)

        # 各論文をエクスポート
        exported_papers = []

        for paper_id in paper_ids:
            if paper_id not in self.catalog['papers']:
                logger.warning(f"Paper not found in catalog: {paper_id}")
                continue

            paper_data = self.catalog['papers'][paper_id]

            # PDFをコピー
            pdf_path = Path(paper_data.get('pdf_path', ''))
            if pdf_path.exists():
                dest_pdf = export_dir / "pdfs" / f"{paper_id}.pdf"
                shutil.copy2(pdf_path, dest_pdf)
                print(f"✓ {paper_id}.pdf")

                # 全文テキスト抽出
                if extract_full_text:
                    try:
                        full_text = self.pdf_processor.extract_text(pdf_path)
                        text_file = export_dir / "texts" / f"{paper_id}.txt"
                        with open(text_file, 'w', encoding='utf-8') as f:
                            f.write(full_text)
                        logger.info(f"Extracted full text: {paper_id}")
                    except Exception as e:
                        logger.error(f"Error extracting text from {paper_id}: {e}")
            else:
                logger.warning(f"PDF not found: {pdf_path}")

            # メタデータをJSON出力
            metadata_file = export_dir / "metadata" / f"{paper_id}.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(paper_data, f, indent=2, ensure_ascii=False)

            exported_papers.append(paper_data)

        # マニフェスト作成
        self._create_manifest(exported_papers, export_dir)

        # RAGインデックス作成
        if create_rag_index:
            self._create_rag_index(exported_papers, export_dir)

        # README作成
        self._create_readme(exported_papers, export_dir)

    def _create_manifest(self, papers: List[Dict], export_dir: Path):
        """マニフェストファイルを作成"""
        manifest = {
            "export_date": datetime.now().isoformat(),
            "total_papers": len(papers),
            "papers": [
                {
                    "paper_id": p['paper_id'],
                    "title": p.get('title', ''),
                    "authors": p.get('authors', []),
                    "year": p.get('year', ''),
                    "perspectives": p.get('perspectives', {})
                }
                for p in papers
            ]
        }

        manifest_path = export_dir / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        logger.info("Created manifest.json")

    def _create_rag_index(self, papers: List[Dict], export_dir: Path):
        """RAG用インデックスファイルを作成"""
        rag_index = {
            "index_version": "1.0",
            "created_at": datetime.now().isoformat(),
            "documents": []
        }

        for paper in papers:
            paper_id = paper['paper_id']
            text_file = export_dir / "texts" / f"{paper_id}.txt"

            # テキストファイルが存在する場合
            if text_file.exists():
                with open(text_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                doc = {
                    "id": paper_id,
                    "title": paper.get('title', ''),
                    "authors": paper.get('authors', []),
                    "year": paper.get('year', ''),
                    "abstract": paper.get('abstract', ''),
                    "content": content[:5000],  # 最初の5000文字
                    "metadata": {
                        "study_type": paper.get('study_type', ''),
                        "perspectives": paper.get('perspectives', {}),
                        "keywords": paper.get('keywords', [])
                    },
                    "file_path": f"texts/{paper_id}.txt"
                }

                rag_index["documents"].append(doc)

        # RAGインデックス保存
        rag_index_path = export_dir / "rag_index.json"
        with open(rag_index_path, 'w', encoding='utf-8') as f:
            json.dump(rag_index, f, indent=2, ensure_ascii=False)

        # RAG設定ファイル作成
        rag_config = {
            "index_file": "rag_index.json",
            "embedding_model": "text-embedding-ada-002",  # 例
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "search_top_k": 5
        }

        rag_config_path = export_dir / "rag_config.json"
        with open(rag_config_path, 'w', encoding='utf-8') as f:
            json.dump(rag_config, f, indent=2, ensure_ascii=False)

        logger.info("Created RAG index and config")

    def _create_readme(self, papers: List[Dict], export_dir: Path):
        """README.mdを作成"""
        content = f"""# Exported Papers

**Export Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Papers**: {len(papers)}

## Papers List

| ID | Title | Authors | Year |
|----|-------|---------|------|
"""

        for paper in papers:
            paper_id = paper['paper_id']
            title = paper.get('title', 'Untitled')
            authors = ', '.join(paper.get('authors', [])[:2])  # 最初の2人
            if len(paper.get('authors', [])) > 2:
                authors += ' et al.'
            year = paper.get('year', '')

            content += f"| {paper_id} | {title} | {authors} | {year} |\n"

        content += """
## Directory Structure

```
.
├── README.md              # This file
├── manifest.json          # Export manifest
├── rag_index.json         # RAG index
├── rag_config.json        # RAG configuration
├── pdfs/                  # PDF files
│   ├── paper001.pdf
│   └── ...
├── texts/                 # Full text extracts
│   ├── paper001.txt
│   └── ...
└── metadata/              # Metadata JSON files
    ├── paper001.json
    └── ...
```

## Usage

### For RAG Systems

Use `rag_index.json` and `rag_config.json` to integrate with your RAG system.

### For Analysis

Metadata files in `metadata/` directory contain structured information about each paper.

---

Generated by 医学論文管理システム
"""

        readme_path = export_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info("Created README.md")


def main():
    """メイン関数"""
    import argparse

    parser = argparse.ArgumentParser(description='医学論文管理システム - エクスポート')
    parser.add_argument('selection_note', type=str, help='選択ノートのパス')
    parser.add_argument('export_dir', type=str, help='エクスポート先ディレクトリ')
    parser.add_argument('--no-text', action='store_true',
                       help='全文テキスト抽出をスキップ')
    parser.add_argument('--no-rag', action='store_true',
                       help='RAGインデックス作成をスキップ')

    args = parser.parse_args()

    selection_note_path = Path(args.selection_note)
    export_dir = Path(args.export_dir)

    exporter = PaperExporter()
    exporter.export_from_selection_note(
        selection_note_path,
        export_dir,
        extract_full_text=not args.no_text,
        create_rag_index=not args.no_rag
    )


if __name__ == "__main__":
    main()
