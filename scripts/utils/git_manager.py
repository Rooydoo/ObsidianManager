"""
Git管理ユーティリティ

自動コミット・プッシュ機能を提供
"""

import subprocess
from pathlib import Path
from typing import List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class GitManager:
    """Git操作管理クラス"""

    def __init__(self, repo_path: Path, enabled: bool = True,
                 auto_commit: bool = True, auto_push: bool = False,
                 remote: str = "origin", branch: str = "main"):
        """
        Args:
            repo_path: Gitリポジトリのパス
            enabled: Git機能を使用するか
            auto_commit: 自動コミットするか
            auto_push: 自動プッシュするか
            remote: リモート名
            branch: ブランチ名
        """
        self.repo_path = repo_path
        self.enabled = enabled
        self.auto_commit = auto_commit
        self.auto_push = auto_push
        self.remote = remote
        self.branch = branch

        if self.enabled:
            self._verify_git_repo()

    def _verify_git_repo(self):
        """Gitリポジトリが存在するか確認"""
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            logger.warning(f"Git repository not found at {self.repo_path}")
            logger.warning("Disabling Git features")
            self.enabled = False

    def _run_command(self, command: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """
        Gitコマンドを実行

        Args:
            command: 実行するコマンド（リスト形式）
            check: エラー時に例外を発生させるか

        Returns:
            実行結果
        """
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {' '.join(command)}")
            logger.error(f"Error: {e.stderr}")
            raise

    def add_files(self, files: List[str]):
        """
        ファイルをステージングエリアに追加

        Args:
            files: 追加するファイルのリスト
        """
        if not self.enabled:
            return

        try:
            for file in files:
                self._run_command(["git", "add", file])
                logger.info(f"Added to git: {file}")
        except Exception as e:
            logger.error(f"Error adding files to git: {e}")

    def commit(self, message: str, files: Optional[List[str]] = None):
        """
        変更をコミット

        Args:
            message: コミットメッセージ
            files: コミットするファイルのリスト（Noneの場合は全変更）
        """
        if not self.enabled or not self.auto_commit:
            logger.info("Auto-commit is disabled, skipping commit")
            return

        try:
            # ファイルを追加
            if files:
                self.add_files(files)
            else:
                # 全変更を追加
                self._run_command(["git", "add", "."])

            # コミット
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            full_message = f"{message}\n\nTimestamp: {timestamp}"

            result = self._run_command(["git", "commit", "-m", full_message], check=False)

            if result.returncode == 0:
                logger.info(f"Committed: {message}")
            else:
                logger.info("No changes to commit")

        except Exception as e:
            logger.error(f"Error committing changes: {e}")

    def push(self):
        """変更をリモートにプッシュ"""
        if not self.enabled or not self.auto_push:
            logger.info("Auto-push is disabled, skipping push")
            return

        try:
            logger.info(f"Pushing to {self.remote}/{self.branch}...")
            result = self._run_command(["git", "push", "-u", self.remote, self.branch])

            if result.returncode == 0:
                logger.info("Successfully pushed to remote")
            else:
                logger.warning("Push failed, continuing...")

        except Exception as e:
            logger.error(f"Error pushing to remote: {e}")
            logger.warning("Continuing without push...")

    def commit_and_push(self, message: str, files: Optional[List[str]] = None):
        """
        コミットとプッシュを実行

        Args:
            message: コミットメッセージ
            files: コミットするファイルのリスト
        """
        self.commit(message, files)

        if self.auto_push:
            self.push()

    def get_status(self) -> str:
        """
        Gitステータスを取得

        Returns:
            git statusの出力
        """
        if not self.enabled:
            return "Git is disabled"

        try:
            result = self._run_command(["git", "status", "--short"])
            return result.stdout
        except Exception as e:
            logger.error(f"Error getting git status: {e}")
            return ""

    def is_clean(self) -> bool:
        """
        作業ツリーがクリーンか確認

        Returns:
            クリーンならTrue
        """
        if not self.enabled:
            return True

        status = self.get_status()
        return len(status.strip()) == 0

    def get_current_branch(self) -> str:
        """
        現在のブランチ名を取得

        Returns:
            ブランチ名
        """
        if not self.enabled:
            return ""

        try:
            result = self._run_command(["git", "branch", "--show-current"])
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Error getting current branch: {e}")
            return ""
