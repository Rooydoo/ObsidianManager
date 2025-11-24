"""
タグシステムユーティリティ

タグの正規化、エイリアス管理、グルーピング機能を提供
"""

import json
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class TagSystem:
    """タグ管理システムクラス"""

    def __init__(self, tag_hierarchy_path: Path, tag_groups_path: Path):
        """
        Args:
            tag_hierarchy_path: tag_hierarchy.jsonのパス
            tag_groups_path: tag_groups.jsonのパス
        """
        self.tag_hierarchy_path = tag_hierarchy_path
        self.tag_groups_path = tag_groups_path

        self.tag_hierarchy = self._load_json(tag_hierarchy_path)
        self.tag_groups = self._load_json(tag_groups_path)

        # 逆引き辞書を構築（エイリアス → 正規タグ）
        self._build_reverse_alias_map()

    def _load_json(self, path: Path) -> Dict:
        """JSONファイルを読み込み"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"File not found: {path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {path}: {e}")
            raise

    def _save_json(self, data: Dict, path: Path):
        """JSONファイルに保存"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved to {path}")
        except Exception as e:
            logger.error(f"Error saving to {path}: {e}")
            raise

    def _build_reverse_alias_map(self):
        """エイリアス→正規タグの逆引きマップを構築"""
        self.alias_to_canonical = {}

        for meta_tag, meta_data in self.tag_hierarchy.items():
            if "aliases" in meta_data:
                for canonical, aliases in meta_data["aliases"].items():
                    # 正規タグ自身もマップに含める
                    self.alias_to_canonical[canonical.lower()] = canonical

                    # エイリアスを登録
                    for alias in aliases:
                        self.alias_to_canonical[alias.lower()] = canonical

    def normalize_tag(self, tag: str, meta_tag: str) -> str:
        """
        タグを正規化（エイリアス → 正規タグ）

        Args:
            tag: 正規化するタグ
            meta_tag: メタタグ（study_type, disease, method, analysis, population）

        Returns:
            正規化されたタグ
        """
        tag_lower = tag.lower().strip()

        # エイリアスマップから検索
        if tag_lower in self.alias_to_canonical:
            canonical = self.alias_to_canonical[tag_lower]
            if canonical != tag:
                logger.info(f"Normalized '{tag}' -> '{canonical}'")
            return canonical

        # 見つからない場合は小文字・アンダースコア形式に変換
        normalized = tag_lower.replace(" ", "_").replace("-", "_")
        logger.warning(f"Tag '{tag}' not found in hierarchy, using normalized form: '{normalized}'")
        return normalized

    def normalize_tags(self, tags: Dict[str, str]) -> Dict[str, str]:
        """
        複数のタグを一括正規化

        Args:
            tags: {meta_tag: tag_value} の辞書

        Returns:
            正規化されたタグ辞書
        """
        normalized = {}
        for meta_tag, tag_value in tags.items():
            if tag_value:
                normalized[meta_tag] = self.normalize_tag(tag_value, meta_tag)
            else:
                normalized[meta_tag] = ""

        return normalized

    def get_canonical_tags(self, meta_tag: str) -> List[str]:
        """
        指定されたメタタグの正規タグリストを取得

        Args:
            meta_tag: メタタグ名

        Returns:
            正規タグのリスト
        """
        if meta_tag in self.tag_hierarchy:
            return self.tag_hierarchy[meta_tag].get("canonical_tags", [])
        else:
            logger.warning(f"Unknown meta_tag: {meta_tag}")
            return []

    def get_aliases(self, canonical_tag: str) -> List[str]:
        """
        正規タグのエイリアスリストを取得

        Args:
            canonical_tag: 正規タグ

        Returns:
            エイリアスのリスト
        """
        for meta_tag, meta_data in self.tag_hierarchy.items():
            if "aliases" in meta_data and canonical_tag in meta_data["aliases"]:
                return meta_data["aliases"][canonical_tag]

        return []

    def get_tag_group(self, tag: str) -> Optional[str]:
        """
        タグが属するグループ名を取得

        Args:
            tag: タグ

        Returns:
            グループ名（見つからない場合はNone）
        """
        for group_name, group_data in self.tag_groups.items():
            if tag in group_data.get("tags", []):
                return group_name

        return None

    def get_group_tags(self, group_name: str) -> List[str]:
        """
        グループに属する全タグを取得

        Args:
            group_name: グループ名

        Returns:
            タグのリスト
        """
        if group_name in self.tag_groups:
            return self.tag_groups[group_name].get("tags", [])
        else:
            logger.warning(f"Unknown group: {group_name}")
            return []

    def get_related_tags(self, tag: str, meta_tag: str) -> List[str]:
        """
        関連タグを取得（同じグループのタグ）

        Args:
            tag: 基準タグ
            meta_tag: メタタグ

        Returns:
            関連タグのリスト
        """
        group_name = self.get_tag_group(tag)
        if group_name:
            group_tags = self.get_group_tags(group_name)
            # 自分自身を除外
            return [t for t in group_tags if t != tag]
        else:
            return []

    def add_tag_to_hierarchy(self, meta_tag: str, canonical_tag: str, aliases: Optional[List[str]] = None):
        """
        新しいタグをヒエラルキーに追加

        Args:
            meta_tag: メタタグ
            canonical_tag: 正規タグ
            aliases: エイリアスのリスト
        """
        if meta_tag not in self.tag_hierarchy:
            logger.error(f"Unknown meta_tag: {meta_tag}")
            return

        # canonical_tagsに追加
        if canonical_tag not in self.tag_hierarchy[meta_tag]["canonical_tags"]:
            self.tag_hierarchy[meta_tag]["canonical_tags"].append(canonical_tag)
            logger.info(f"Added canonical tag '{canonical_tag}' to {meta_tag}")

        # エイリアスを追加
        if aliases:
            if "aliases" not in self.tag_hierarchy[meta_tag]:
                self.tag_hierarchy[meta_tag]["aliases"] = {}

            if canonical_tag not in self.tag_hierarchy[meta_tag]["aliases"]:
                self.tag_hierarchy[meta_tag]["aliases"][canonical_tag] = []

            for alias in aliases:
                if alias not in self.tag_hierarchy[meta_tag]["aliases"][canonical_tag]:
                    self.tag_hierarchy[meta_tag]["aliases"][canonical_tag].append(alias)
                    logger.info(f"Added alias '{alias}' for '{canonical_tag}'")

        # ファイルに保存
        self._save_json(self.tag_hierarchy, self.tag_hierarchy_path)

        # 逆引きマップを再構築
        self._build_reverse_alias_map()

    def create_tag_group(self, group_name: str, meta_tag: str, tags: List[str],
                        display_name: str, description: str = ""):
        """
        新しいタググループを作成

        Args:
            group_name: グループ名（識別子）
            meta_tag: メタタグ
            tags: グループに含めるタグのリスト
            display_name: 表示名
            description: 説明
        """
        if group_name in self.tag_groups:
            logger.warning(f"Group '{group_name}' already exists, updating...")

        self.tag_groups[group_name] = {
            "meta_tag": meta_tag,
            "display_name": display_name,
            "tags": tags,
            "description": description
        }

        # ファイルに保存
        self._save_json(self.tag_groups, self.tag_groups_path)
        logger.info(f"Created/updated tag group '{group_name}'")

    def suggest_groups_from_cooccurrence(self, catalog_data: Dict, min_cooccurrence: int = 3) -> List[Dict]:
        """
        タグの共起パターンから新しいグループを提案

        Args:
            catalog_data: catalog.jsonのデータ
            min_cooccurrence: グループ提案の最小共起回数

        Returns:
            提案グループのリスト
        """
        # メタタグごとにタグの共起を集計
        cooccurrence = defaultdict(lambda: defaultdict(int))

        for paper_id, paper_data in catalog_data.get("papers", {}).items():
            perspectives = paper_data.get("perspectives", {})

            for meta_tag in ["disease", "method", "analysis", "population"]:
                if meta_tag in perspectives:
                    tag = perspectives[meta_tag]
                    if tag and tag != "not_applicable":
                        # 他のメタタグのタグとの共起をカウント
                        for other_meta, other_tag in perspectives.items():
                            if other_meta != meta_tag and other_tag and other_tag != "not_applicable":
                                cooccurrence[meta_tag][f"{tag}+{other_tag}"] += 1

        # 提案を生成
        suggestions = []
        for meta_tag, pairs in cooccurrence.items():
            for pair, count in pairs.items():
                if count >= min_cooccurrence:
                    tags = pair.split("+")
                    suggestions.append({
                        "meta_tag": meta_tag,
                        "tags": tags,
                        "count": count
                    })

        return sorted(suggestions, key=lambda x: x["count"], reverse=True)

    def validate_tag(self, tag: str, meta_tag: str) -> Tuple[bool, str]:
        """
        タグの妥当性を検証

        Args:
            tag: 検証するタグ
            meta_tag: メタタグ

        Returns:
            (is_valid, message) のタプル
        """
        if not tag:
            return False, "Tag cannot be empty"

        canonical_tags = self.get_canonical_tags(meta_tag)

        # 正規タグに存在するか
        if tag in canonical_tags:
            return True, "Valid canonical tag"

        # エイリアスとして存在するか
        normalized = self.normalize_tag(tag, meta_tag)
        if normalized in canonical_tags:
            return True, f"Valid alias (normalized to '{normalized}')"

        # 新規タグ
        return True, f"New tag (will be added to hierarchy)"
