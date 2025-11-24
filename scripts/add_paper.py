#!/usr/bin/env python3
"""
論文追加スクリプト

PDFを読み込み、メタデータを入力し、Obsidianノートを生成する
"""

import sys
import json
import yaml
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils import PDFProcessor, TagSystem, GitManager

# ロガー設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PaperAdder:
    """論文追加管理クラス"""

    def __init__(self, config_path: Path):
        """
        Args:
            config_path: config.yamlのパス
        """
        self.config = self._load_config(config_path)
        self.project_root = project_root

        # パス設定
        self.papers_dir = self.project_root / self.config['paths']['papers_dir']
        self.vault_dir = self.project_root / self.config['paths']['obsidian_vault']
        self.catalog_path = self.project_root / self.config['paths']['catalog']
        self.tag_hierarchy_path = self.project_root / self.config['paths']['tag_hierarchy']
        self.tag_groups_path = self.project_root / self.config['paths']['tag_groups']

        # ディレクトリ作成
        self.papers_dir.mkdir(parents=True, exist_ok=True)
        (self.vault_dir / "Papers").mkdir(parents=True, exist_ok=True)
        (self.vault_dir / "MOC").mkdir(parents=True, exist_ok=True)

        # ユーティリティ初期化
        self.pdf_processor = PDFProcessor(
            extractor=self.config['processing']['pdf']['extractor']
        )
        self.tag_system = TagSystem(self.tag_hierarchy_path, self.tag_groups_path)
        self.git_manager = GitManager(
            repo_path=self.project_root,
            enabled=self.config['git']['enabled'],
            auto_commit=self.config['git']['auto_commit'],
            auto_push=self.config['git']['auto_push'],
            remote=self.config['git']['remote'],
            branch=self.config['git']['branch']
        )

        # カタログ読み込み
        self.catalog = self._load_catalog()

    def _load_config(self, config_path: Path) -> Dict:
        """設定ファイルを読み込み"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _load_catalog(self) -> Dict:
        """カタログを読み込み"""
        if self.catalog_path.exists():
            with open(self.catalog_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "papers": {},
                "metadata": {
                    "total_papers": 0,
                    "last_updated": None,
                    "study_type_distribution": {},
                    "disease_distribution": {},
                    "method_distribution": {},
                    "analysis_distribution": {},
                    "population_distribution": {}
                }
            }

    def _save_catalog(self):
        """カタログを保存"""
        with open(self.catalog_path, 'w', encoding='utf-8') as f:
            json.dump(self.catalog, f, indent=2, ensure_ascii=False)
        logger.info("Catalog saved")

    def _generate_paper_id(self) -> str:
        """新しいpaper IDを生成"""
        existing_ids = list(self.catalog['papers'].keys())
        if not existing_ids:
            return "paper001"

        # 最大のIDを見つける
        max_num = 0
        for paper_id in existing_ids:
            if paper_id.startswith("paper"):
                try:
                    num = int(paper_id.replace("paper", ""))
                    max_num = max(max_num, num)
                except ValueError:
                    continue

        new_id = f"paper{str(max_num + 1).zfill(3)}"
        return new_id

    def add_paper_manual(self, pdf_path: Optional[Path] = None,
                        metadata_yaml: Optional[Path] = None) -> str:
        """
        手動モードで論文を追加

        Args:
            pdf_path: PDFファイルのパス（オプション）
            metadata_yaml: メタデータYAMLファイルのパス（オプション）

        Returns:
            生成されたpaper_id
        """
        print("\n" + "="*60)
        print("論文追加 - 手動モード")
        print("="*60 + "\n")

        # メタデータ入力
        if metadata_yaml and metadata_yaml.exists():
            print(f"メタデータファイルから読み込み: {metadata_yaml}")
            with open(metadata_yaml, 'r', encoding='utf-8') as f:
                metadata = yaml.safe_load(f)
        else:
            metadata = self._input_metadata_interactive()

        # Paper ID生成
        paper_id = self._generate_paper_id()
        metadata['paper_id'] = paper_id

        print(f"\n生成されたPaper ID: {paper_id}")

        # PDFファイル処理
        if pdf_path and pdf_path.exists():
            dest_path = self.papers_dir / f"{paper_id}.pdf"
            shutil.copy2(pdf_path, dest_path)
            metadata['pdf_path'] = str(dest_path.absolute())
            print(f"PDFをコピー: {dest_path}")

            # アブストラクト抽出（メタデータに含まれていない場合）
            if not metadata.get('abstract'):
                print("\nPDFからアブストラクトを抽出中...")
                abstract = self.pdf_processor.extract_abstract(dest_path)
                if abstract:
                    metadata['abstract'] = abstract
                    print("アブストラクトを抽出しました")
                else:
                    print("アブストラクトを自動抽出できませんでした")
        else:
            metadata['pdf_path'] = ""

        # タグ正規化
        if 'perspectives' in metadata:
            metadata['perspectives'] = self.tag_system.normalize_tags(
                metadata['perspectives']
            )

        # タイムスタンプ
        now = datetime.now().isoformat()
        metadata['date_added'] = now
        metadata['date_modified'] = now

        # カタログに追加
        self.catalog['papers'][paper_id] = metadata
        self._update_catalog_metadata()
        self._save_catalog()

        # Obsidianノート生成
        self._create_obsidian_note(paper_id, metadata)

        # MOC更新
        self._update_moc_notes(metadata)

        # Git コミット
        files_to_commit = [
            str(self.catalog_path.relative_to(self.project_root)),
            f"ObsidianVault/Papers/{paper_id}.md"
        ]
        self.git_manager.commit(
            f"Add paper: {metadata.get('title', paper_id)}",
            files_to_commit
        )

        print("\n" + "="*60)
        print(f"✓ 論文を追加しました: {paper_id}")
        print(f"✓ Obsidianノート: ObsidianVault/Papers/{paper_id}.md")
        print("="*60 + "\n")

        return paper_id

    def _input_metadata_interactive(self) -> Dict[str, Any]:
        """対話的にメタデータを入力"""
        print("基本情報を入力してください:\n")

        metadata = {}

        # 基本情報
        metadata['title'] = input("タイトル: ").strip()
        authors_str = input("著者（カンマ区切り）: ").strip()
        metadata['authors'] = [a.strip() for a in authors_str.split(',') if a.strip()]

        year_str = input("年: ").strip()
        metadata['year'] = int(year_str) if year_str else None

        metadata['journal'] = input("ジャーナル名: ").strip()
        metadata['volume'] = input("巻: ").strip()
        metadata['issue'] = input("号: ").strip()
        metadata['pages'] = input("ページ: ").strip()
        metadata['doi'] = input("DOI: ").strip()
        metadata['pmid'] = input("PMID: ").strip()

        # 研究デザイン
        print("\n研究デザイン:")
        study_types = self.tag_system.get_canonical_tags('study_type')
        print("\n選択肢:")
        for i, st in enumerate(study_types, 1):
            print(f"  {i}. {st}")

        study_type_input = input("\n研究タイプ（番号または名前）: ").strip()
        if study_type_input.isdigit():
            idx = int(study_type_input) - 1
            if 0 <= idx < len(study_types):
                metadata['study_type'] = study_types[idx]
        else:
            metadata['study_type'] = study_type_input

        metadata['study_design'] = input("研究デザイン詳細: ").strip()

        sample_size_str = input("サンプルサイズ: ").strip()
        metadata['sample_size'] = int(sample_size_str) if sample_size_str else None

        metadata['study_population'] = input("対象集団: ").strip()

        # Perspectives
        print("\n分類（Perspectives）:")
        perspectives = {}
        perspectives['study_type'] = metadata['study_type']

        for meta_tag in ['disease', 'method', 'analysis', 'population']:
            print(f"\n{meta_tag.upper()} tags:")
            tags = self.tag_system.get_canonical_tags(meta_tag)
            print("選択肢（一部）:", ", ".join(tags[:10]))
            if len(tags) > 10:
                print(f"  ... 他 {len(tags) - 10} 個")

            tag_input = input(f"{meta_tag}タグ: ").strip()
            perspectives[meta_tag] = tag_input if tag_input else "not_applicable"

        metadata['perspectives'] = perspectives

        # キーワード
        keywords_str = input("\nキーワード（カンマ区切り）: ").strip()
        metadata['keywords'] = [k.strip() for k in keywords_str.split(',') if k.strip()]

        # その他
        metadata['language'] = input("言語（en/ja）[en]: ").strip() or "en"
        metadata['read_status'] = "unread"
        metadata['priority'] = input("優先度（low/medium/high）[medium]: ").strip() or "medium"

        # アブストラクト・要約
        print("\nアブストラクト（複数行入力、最後に空行で終了）:")
        abstract_lines = []
        while True:
            line = input()
            if not line:
                break
            abstract_lines.append(line)
        metadata['abstract'] = "\n".join(abstract_lines) if abstract_lines else ""

        print("\n要約（複数行入力、最後に空行で終了）:")
        summary_lines = []
        while True:
            line = input()
            if not line:
                break
            summary_lines.append(line)
        metadata['summary'] = "\n".join(summary_lines) if summary_lines else ""

        return metadata

    def _update_catalog_metadata(self):
        """カタログのメタデータを更新"""
        papers = self.catalog['papers']
        metadata = self.catalog['metadata']

        metadata['total_papers'] = len(papers)
        metadata['last_updated'] = datetime.now().isoformat()

        # 分布を集計
        for dist_key in ['study_type', 'disease', 'method', 'analysis', 'population']:
            distribution = {}
            for paper_data in papers.values():
                perspectives = paper_data.get('perspectives', {})
                if dist_key in perspectives:
                    tag = perspectives[dist_key]
                    if tag:
                        distribution[tag] = distribution.get(tag, 0) + 1

            metadata[f'{dist_key}_distribution'] = distribution

    def _create_obsidian_note(self, paper_id: str, metadata: Dict[str, Any]):
        """Obsidianノートを作成"""
        note_path = self.vault_dir / "Papers" / f"{paper_id}.md"

        # ノート内容を生成
        content = self._generate_note_content(metadata)

        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Created Obsidian note: {note_path}")

    def _generate_note_content(self, metadata: Dict[str, Any]) -> str:
        """ノート内容を生成"""
        # YAML frontmatter
        frontmatter = {
            'paper_id': metadata.get('paper_id'),
            'title': metadata.get('title'),
            'authors': metadata.get('authors', []),
            'year': metadata.get('year'),
            'journal': metadata.get('journal'),
            'volume': metadata.get('volume'),
            'issue': metadata.get('issue'),
            'pages': metadata.get('pages'),
            'doi': metadata.get('doi'),
            'pmid': metadata.get('pmid'),
            'pdf_path': metadata.get('pdf_path'),
            'study_type': metadata.get('study_type'),
            'study_design': metadata.get('study_design'),
            'sample_size': metadata.get('sample_size'),
            'study_population': metadata.get('study_population'),
            'perspectives': metadata.get('perspectives', {}),
            'keywords': metadata.get('keywords', []),
            'language': metadata.get('language'),
            'date_added': metadata.get('date_added'),
            'date_modified': metadata.get('date_modified'),
            'read_status': metadata.get('read_status'),
            'priority': metadata.get('priority'),
        }

        # タグリスト生成
        tags = []
        if metadata.get('perspectives'):
            for tag_value in metadata['perspectives'].values():
                if tag_value and tag_value != "not_applicable":
                    tags.append(f"#{tag_value}")

        frontmatter['tags'] = tags

        # YAMLをダンプ
        yaml_str = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)

        # ノート本文
        title = metadata.get('title', 'Untitled')
        authors = metadata.get('authors', [])
        authors_str = ", ".join(authors) if authors else "Unknown"
        year = metadata.get('year', '')
        journal = metadata.get('journal', '')

        study_type = metadata.get('study_type', '')
        study_design = metadata.get('study_design', '')
        sample_size = metadata.get('sample_size', '')
        study_population = metadata.get('study_population', '')

        abstract = metadata.get('abstract', '')
        summary = metadata.get('summary', '')

        perspectives = metadata.get('perspectives', {})

        content = f"""---
{yaml_str}---

# {title}

## 📊 Study Overview

**研究タイプ**: {study_type} / {study_design}
**対象**: {study_population} (n={sample_size})
**著者**: {authors_str}
**掲載誌**: {journal} ({year})

---

## 📝 Summary（要約）

{summary if summary else '（要約なし）'}

---

## 📄 Abstract（原文）

<details>
<summary>クリックで展開</summary>

{abstract if abstract else '（アブストラクトなし）'}

</details>

---

## 🔍 Key Findings

### 主要な知見
（ここに主要な知見を記載）

### 限界・課題
（ここに限界・課題を記載）

---

## 🔗 Related Information

### Perspectives
"""

        # Perspectives リンク
        if perspectives.get('disease') and perspectives['disease'] != 'not_applicable':
            content += f"- **Disease**: [[{perspectives['disease']}_view]]\n"
        if perspectives.get('method') and perspectives['method'] != 'not_applicable':
            content += f"- **Method**: [[{perspectives['method']}_view]]\n"
        if perspectives.get('analysis') and perspectives['analysis'] != 'not_applicable':
            content += f"- **Analysis**: [[{perspectives['analysis']}_view]]\n"
        if perspectives.get('study_type'):
            content += f"- **Study Type**: [[{perspectives['study_type']}_view]]\n"

        content += """
### Related Papers
（関連論文へのリンク）

---

## 📎 Resources

### PDF
"""

        if metadata.get('pdf_path'):
            content += f"[📄 Open PDF](file://{metadata['pdf_path']})\n"

        content += """
### Links
"""

        if metadata.get('doi'):
            content += f"- DOI: [{metadata['doi']}](https://doi.org/{metadata['doi']})\n"
        if metadata.get('pmid'):
            content += f"- PubMed: [PMID: {metadata['pmid']}](https://pubmed.ncbi.nlm.nih.gov/{metadata['pmid']}/)\n"

        content += """
---

## 💡 Personal Notes

### 読んだ日: [YYYY-MM-DD]

### メモ
- [ ] TODO項目

### 疑問点
（疑問点を記載）

### 引用候補
（引用候補セクション）

---

## 🔄 Update History

"""
        content += f"- {metadata.get('date_added', '')[:10]}: 初回作成\n"

        return content

    def _update_moc_notes(self, metadata: Dict[str, Any]):
        """MOCノートを更新"""
        perspectives = metadata.get('perspectives', {})

        # 各perspectiveのMOCを更新（存在しない場合は作成）
        for meta_tag, tag_value in perspectives.items():
            if tag_value and tag_value != "not_applicable":
                self._create_or_update_moc(meta_tag, tag_value)

    def _create_or_update_moc(self, meta_tag: str, tag_value: str):
        """MOCノートを作成または更新"""
        moc_filename = f"{tag_value}_view.md"
        moc_path = self.vault_dir / "MOC" / moc_filename

        if not moc_path.exists():
            # 新規作成
            content = f"""# {tag_value.replace('_', ' ').title()} View ({meta_tag.title()} Perspective)

## Papers in this category

```dataview
TABLE title, authors, year, study_type
FROM "Papers"
WHERE perspectives.{meta_tag} = "{tag_value}"
SORT year DESC
```

## By Year

```dataview
TABLE rows.title as "Papers"
FROM "Papers"
WHERE perspectives.{meta_tag} = "{tag_value}"
GROUP BY year
SORT year DESC
```

## Related Perspectives

（関連する他のperspectiveへのリンク）

---

**Last updated**: {datetime.now().strftime('%Y-%m-%d')}
"""

            with open(moc_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Created MOC: {moc_path}")


def main():
    """メイン関数"""
    import argparse

    parser = argparse.ArgumentParser(description='医学論文管理システム - 論文追加')
    parser.add_argument('--pdf', type=str, help='PDFファイルのパス')
    parser.add_argument('--metadata', type=str, help='メタデータYAMLファイルのパス')
    parser.add_argument('--config', type=str,
                       default='config/config.yaml',
                       help='設定ファイルのパス')

    args = parser.parse_args()

    # パス変換
    config_path = project_root / args.config
    pdf_path = Path(args.pdf) if args.pdf else None
    metadata_path = Path(args.metadata) if args.metadata else None

    # 論文追加
    adder = PaperAdder(config_path)
    paper_id = adder.add_paper_manual(pdf_path, metadata_path)

    print(f"\n完了: {paper_id}")


if __name__ == "__main__":
    main()
