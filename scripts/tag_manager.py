#!/usr/bin/env python3
"""
タグ管理ツール

タグの追加、グループ提案、共起分析などを実行
"""

import sys
import json
from pathlib import Path
from typing import List, Dict
import logging

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils import TagSystem

# ロガー設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TagManager:
    """タグ管理クラス"""

    def __init__(self):
        self.project_root = project_root
        self.tag_hierarchy_path = project_root / "data" / "tag_hierarchy.json"
        self.tag_groups_path = project_root / "data" / "tag_groups.json"
        self.catalog_path = project_root / "data" / "catalog.json"

        self.tag_system = TagSystem(self.tag_hierarchy_path, self.tag_groups_path)

    def list_tags(self, meta_tag: str = None):
        """タグ一覧を表示"""
        print("\n" + "="*60)
        print("タグ一覧")
        print("="*60 + "\n")

        if meta_tag:
            # 特定のメタタグのみ
            self._print_meta_tag_info(meta_tag)
        else:
            # 全メタタグ
            for mt in ['study_type', 'disease', 'method', 'analysis', 'population']:
                self._print_meta_tag_info(mt)
                print()

    def _print_meta_tag_info(self, meta_tag: str):
        """メタタグの情報を表示"""
        print(f"[{meta_tag.upper()}]")
        canonical_tags = self.tag_system.get_canonical_tags(meta_tag)

        for tag in canonical_tags:
            aliases = self.tag_system.get_aliases(tag)
            group = self.tag_system.get_tag_group(tag)

            print(f"  • {tag}")
            if aliases:
                print(f"    エイリアス: {', '.join(aliases)}")
            if group:
                print(f"    グループ: {group}")

    def add_tag(self, meta_tag: str, canonical_tag: str, aliases: List[str] = None):
        """新しいタグを追加"""
        print(f"\nタグを追加: {canonical_tag} ({meta_tag})")

        if aliases:
            print(f"エイリアス: {', '.join(aliases)}")

        confirm = input("\n追加しますか? (y/n): ").strip().lower()
        if confirm == 'y':
            self.tag_system.add_tag_to_hierarchy(meta_tag, canonical_tag, aliases)
            print("✓ タグを追加しました")
        else:
            print("キャンセルしました")

    def suggest_groups(self, min_cooccurrence: int = 3):
        """共起パターンからグループを提案"""
        print("\n" + "="*60)
        print("タググループ提案（共起分析）")
        print("="*60 + "\n")

        # カタログ読み込み
        with open(self.catalog_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)

        # 提案を生成
        suggestions = self.tag_system.suggest_groups_from_cooccurrence(
            catalog, min_cooccurrence
        )

        if not suggestions:
            print("提案するグループはありません")
            return

        print(f"共起回数 {min_cooccurrence} 回以上のタグペア:\n")

        for i, suggestion in enumerate(suggestions[:10], 1):  # 上位10件
            print(f"{i}. {suggestion['meta_tag']}: {' + '.join(suggestion['tags'])}")
            print(f"   共起回数: {suggestion['count']}")
            print()

    def list_groups(self):
        """グループ一覧を表示"""
        print("\n" + "="*60)
        print("タググループ一覧")
        print("="*60 + "\n")

        groups = self.tag_system.tag_groups

        for group_name, group_data in groups.items():
            print(f"[{group_name}]")
            print(f"  表示名: {group_data.get('display_name', '')}")
            print(f"  メタタグ: {group_data.get('meta_tag', '')}")
            print(f"  説明: {group_data.get('description', '')}")
            print(f"  タグ: {', '.join(group_data.get('tags', []))}")
            print()

    def create_group(self, group_name: str, meta_tag: str,
                    tags: List[str], display_name: str, description: str = ""):
        """新しいグループを作成"""
        print(f"\nグループを作成: {group_name}")
        print(f"表示名: {display_name}")
        print(f"メタタグ: {meta_tag}")
        print(f"タグ: {', '.join(tags)}")
        print(f"説明: {description}")

        confirm = input("\n作成しますか? (y/n): ").strip().lower()
        if confirm == 'y':
            self.tag_system.create_tag_group(
                group_name, meta_tag, tags, display_name, description
            )
            print("✓ グループを作成しました")
        else:
            print("キャンセルしました")

    def show_statistics(self):
        """タグの統計情報を表示"""
        print("\n" + "="*60)
        print("タグ統計")
        print("="*60 + "\n")

        # カタログ読み込み
        with open(self.catalog_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)

        metadata = catalog.get('metadata', {})

        print(f"総論文数: {metadata.get('total_papers', 0)}")
        print()

        # 各メタタグの分布
        for dist_key in ['study_type', 'disease', 'method', 'analysis', 'population']:
            dist_data = metadata.get(f'{dist_key}_distribution', {})
            if dist_data:
                print(f"[{dist_key.upper()} 分布]")
                sorted_items = sorted(dist_data.items(), key=lambda x: x[1], reverse=True)
                for tag, count in sorted_items[:10]:  # 上位10件
                    print(f"  {tag}: {count}")
                print()


def main():
    """メイン関数"""
    import argparse

    parser = argparse.ArgumentParser(description='医学論文管理システム - タグ管理')
    subparsers = parser.add_subparsers(dest='command', help='コマンド')

    # list コマンド
    parser_list = subparsers.add_parser('list', help='タグ一覧を表示')
    parser_list.add_argument('--meta-tag', type=str, help='表示するメタタグ')

    # add コマンド
    parser_add = subparsers.add_parser('add', help='タグを追加')
    parser_add.add_argument('meta_tag', type=str, help='メタタグ')
    parser_add.add_argument('canonical_tag', type=str, help='正規タグ')
    parser_add.add_argument('--aliases', type=str, nargs='+', help='エイリアス')

    # suggest-groups コマンド
    parser_suggest = subparsers.add_parser('suggest-groups', help='グループを提案')
    parser_suggest.add_argument('--min-cooccurrence', type=int, default=3,
                               help='最小共起回数')

    # list-groups コマンド
    parser_list_groups = subparsers.add_parser('list-groups', help='グループ一覧')

    # create-group コマンド
    parser_create_group = subparsers.add_parser('create-group', help='グループを作成')
    parser_create_group.add_argument('group_name', type=str, help='グループ名')
    parser_create_group.add_argument('meta_tag', type=str, help='メタタグ')
    parser_create_group.add_argument('display_name', type=str, help='表示名')
    parser_create_group.add_argument('--tags', type=str, nargs='+', required=True,
                                     help='タグのリスト')
    parser_create_group.add_argument('--description', type=str, default='', help='説明')

    # stats コマンド
    parser_stats = subparsers.add_parser('stats', help='統計情報を表示')

    args = parser.parse_args()

    manager = TagManager()

    if args.command == 'list':
        manager.list_tags(args.meta_tag)

    elif args.command == 'add':
        manager.add_tag(args.meta_tag, args.canonical_tag, args.aliases)

    elif args.command == 'suggest-groups':
        manager.suggest_groups(args.min_cooccurrence)

    elif args.command == 'list-groups':
        manager.list_groups()

    elif args.command == 'create-group':
        manager.create_group(
            args.group_name,
            args.meta_tag,
            args.tags,
            args.display_name,
            args.description
        )

    elif args.command == 'stats':
        manager.show_statistics()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
