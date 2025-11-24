"""
PDF処理ユーティリティ

PDFからのテキスト抽出、アブストラクト抽出機能を提供
"""

import PyPDF2
import pdfplumber
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    """PDF処理クラス"""

    def __init__(self, extractor: str = "pdfplumber"):
        """
        Args:
            extractor: 使用する抽出ツール ("pdfplumber" or "pypdf2")
        """
        self.extractor = extractor.lower()
        if self.extractor not in ["pdfplumber", "pypdf2"]:
            raise ValueError(f"Invalid extractor: {extractor}")

    def extract_text(self, pdf_path: Path, max_pages: int = 0) -> str:
        """
        PDFから全文テキストを抽出

        Args:
            pdf_path: PDFファイルのパス
            max_pages: 抽出する最大ページ数（0=全ページ）

        Returns:
            抽出されたテキスト
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        logger.info(f"Extracting text from: {pdf_path}")

        if self.extractor == "pdfplumber":
            return self._extract_with_pdfplumber(pdf_path, max_pages)
        else:
            return self._extract_with_pypdf2(pdf_path, max_pages)

    def _extract_with_pdfplumber(self, pdf_path: Path, max_pages: int) -> str:
        """pdfplumberを使用してテキスト抽出"""
        text_parts = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                pages_to_extract = total_pages if max_pages == 0 else min(max_pages, total_pages)

                for i in range(pages_to_extract):
                    page = pdf.pages[i]
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)

                logger.info(f"Extracted {pages_to_extract} pages using pdfplumber")
                return "\n\n".join(text_parts)

        except Exception as e:
            logger.error(f"Error extracting text with pdfplumber: {e}")
            raise

    def _extract_with_pypdf2(self, pdf_path: Path, max_pages: int) -> str:
        """PyPDF2を使用してテキスト抽出"""
        text_parts = []

        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                pages_to_extract = total_pages if max_pages == 0 else min(max_pages, total_pages)

                for i in range(pages_to_extract):
                    page = pdf_reader.pages[i]
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)

                logger.info(f"Extracted {pages_to_extract} pages using PyPDF2")
                return "\n\n".join(text_parts)

        except Exception as e:
            logger.error(f"Error extracting text with PyPDF2: {e}")
            raise

    def extract_abstract(self, pdf_path: Path) -> Optional[str]:
        """
        PDFからアブストラクトを抽出（簡易実装）

        Note: 完全な抽出は困難なため、最初の数ページからAbstract部分を探す

        Args:
            pdf_path: PDFファイルのパス

        Returns:
            抽出されたアブストラクト（見つからない場合はNone）
        """
        logger.info(f"Attempting to extract abstract from: {pdf_path}")

        try:
            # 最初の3ページを抽出
            text = self.extract_text(pdf_path, max_pages=3)

            # "Abstract"または"ABSTRACT"のセクションを探す
            abstract = self._find_abstract_section(text)

            if abstract:
                logger.info("Abstract found and extracted")
                return abstract
            else:
                logger.warning("Abstract section not found")
                return None

        except Exception as e:
            logger.error(f"Error extracting abstract: {e}")
            return None

    def _find_abstract_section(self, text: str) -> Optional[str]:
        """
        テキストからAbstractセクションを抽出

        Args:
            text: 検索対象のテキスト

        Returns:
            抽出されたアブストラクト
        """
        import re

        # Abstractのパターンを探す
        patterns = [
            r'ABSTRACT\s*\n(.*?)\n(?:INTRODUCTION|Introduction|KEYWORDS|Keywords|\n\n[A-Z])',
            r'Abstract\s*\n(.*?)\n(?:Introduction|INTRODUCTION|Keywords|KEYWORDS|\n\n[A-Z])',
            r'要旨\s*\n(.*?)\n(?:はじめに|緒言|キーワード|\n\n)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                abstract = match.group(1).strip()
                # 長さチェック（あまりに短い/長い場合は誤検出の可能性）
                if 100 < len(abstract) < 3000:
                    return abstract

        return None

    def get_pdf_info(self, pdf_path: Path) -> Dict[str, Any]:
        """
        PDFファイルの基本情報を取得

        Args:
            pdf_path: PDFファイルのパス

        Returns:
            PDF情報の辞書
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        info = {
            "file_path": str(pdf_path.absolute()),
            "file_name": pdf_path.name,
            "file_size": pdf_path.stat().st_size,
        }

        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                info["num_pages"] = len(pdf_reader.pages)

                # メタデータ取得（ある場合）
                if pdf_reader.metadata:
                    metadata = pdf_reader.metadata
                    info["title"] = metadata.get("/Title", "")
                    info["author"] = metadata.get("/Author", "")
                    info["subject"] = metadata.get("/Subject", "")
                    info["creator"] = metadata.get("/Creator", "")

        except Exception as e:
            logger.warning(f"Could not extract PDF metadata: {e}")

        return info
