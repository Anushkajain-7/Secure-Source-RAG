"""
SecureSource RAG — PDF Parser

Parses text-based PDFs using PyMuPDF (fitz), preserving:
- File name and page numbers
- Paragraphs and sections
- Table locations
- Document version and dates
- Repeated header/footer detection and removal
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class PDFPage:
    """Content from a single PDF page."""
    page_number: int
    text: str
    tables: list[str] = field(default_factory=list)
    has_images: bool = False
    is_scanned: bool = False


@dataclass
class PDFSection:
    """A logical section from a PDF."""
    heading: str
    content: str
    page_start: int
    page_end: int
    tables: list[str] = field(default_factory=list)


@dataclass
class ParsedPDF:
    """Result of parsing a PDF file."""
    title: str
    source_name: str
    raw_text: str
    pages: list[PDFPage]
    sections: list[PDFSection]
    metadata: dict
    content_hash: str
    total_pages: int = 0
    is_scanned: bool = False
    needs_ocr: bool = False
    errors: list[str] = field(default_factory=list)


def parse_pdf(file_path: str | Path, file_bytes: bytes | None = None) -> ParsedPDF:
    """
    Parse a PDF file using PyMuPDF.

    Args:
        file_path: Path to the PDF file
        file_bytes: Optional pre-loaded bytes

    Returns:
        ParsedPDF with pages, sections, and metadata
    """
    path = Path(file_path)
    errors = []

    try:
        import fitz  # PyMuPDF
    except ImportError:
        return ParsedPDF(
            title=path.stem,
            source_name=path.name,
            raw_text="",
            pages=[],
            sections=[],
            metadata={"source_name": path.name},
            content_hash="",
            errors=["PyMuPDF not installed. Install with: pip install PyMuPDF"],
        )

    try:
        if file_bytes:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        else:
            doc = fitz.open(str(path))
    except Exception as e:
        return ParsedPDF(
            title=path.stem,
            source_name=path.name,
            raw_text="",
            pages=[],
            sections=[],
            metadata={"source_name": path.name},
            content_hash="",
            errors=[f"Failed to open PDF: {e}"],
        )

    # Extract metadata
    pdf_metadata = doc.metadata or {}
    metadata = {
        "source_name": path.name,
        "author": pdf_metadata.get("author", ""),
        "title": pdf_metadata.get("title", ""),
        "subject": pdf_metadata.get("subject", ""),
        "creator": pdf_metadata.get("creator", ""),
        "creation_date": pdf_metadata.get("creationDate", ""),
        "mod_date": pdf_metadata.get("modDate", ""),
        "total_pages": len(doc),
    }

    title = pdf_metadata.get("title", "") or path.stem

    # Extract pages
    pages = []
    all_text_parts = []
    total_text_length = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")

        # Detect tables (simple heuristic)
        tables = _extract_tables_from_page(page)

        # Check for images (scanned PDF indicator)
        images = page.get_images()
        has_images = len(images) > 0

        pages.append(
            PDFPage(
                page_number=page_num + 1,
                text=text,
                tables=tables,
                has_images=has_images,
                is_scanned=has_images and len(text.strip()) < 50,
            )
        )

        all_text_parts.append(text)
        total_text_length += len(text.strip())

    doc.close()

    raw_text = "\n\n".join(all_text_parts)

    # Detect if this is a scanned PDF
    avg_text_per_page = total_text_length / max(len(pages), 1)
    needs_ocr = avg_text_per_page < 100 and any(p.has_images for p in pages)

    # Remove repeated headers/footers
    cleaned_pages = _remove_repeated_headers_footers(pages)

    # Extract sections from text
    sections = _extract_sections(cleaned_pages)

    # Content hash
    content_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()

    return ParsedPDF(
        title=title,
        source_name=path.name,
        raw_text=raw_text,
        pages=cleaned_pages,
        sections=sections,
        metadata=metadata,
        content_hash=content_hash,
        total_pages=len(pages),
        is_scanned=needs_ocr,
        needs_ocr=needs_ocr,
        errors=errors,
    )


def _extract_tables_from_page(page) -> list[str]:
    """Extract tables from a PDF page using simple heuristics."""
    tables = []
    try:
        # PyMuPDF's find_tables (available in newer versions)
        if hasattr(page, "find_tables"):
            found = page.find_tables()
            for table in found:
                table_data = table.extract()
                if table_data:
                    # Convert to text representation
                    rows = []
                    for row in table_data:
                        rows.append(" | ".join(str(cell or "") for cell in row))
                    tables.append("\n".join(rows))
    except Exception:
        pass  # Table extraction is best-effort
    return tables


def _remove_repeated_headers_footers(pages: list[PDFPage]) -> list[PDFPage]:
    """Detect and remove repeated headers/footers across pages."""
    if len(pages) < 3:
        return pages

    # Collect first and last lines from each page
    first_lines = []
    last_lines = []

    for page in pages:
        lines = page.text.strip().split("\n")
        if lines:
            first_lines.append(lines[0].strip())
            last_lines.append(lines[-1].strip())

    # Find repeated first lines (headers)
    header_pattern = _find_repeated_pattern(first_lines)

    # Find repeated last lines (footers)
    footer_pattern = _find_repeated_pattern(last_lines)

    # Remove them
    cleaned = []
    for page in pages:
        text = page.text
        if header_pattern:
            lines = text.split("\n")
            if lines and lines[0].strip() == header_pattern:
                text = "\n".join(lines[1:])
        if footer_pattern:
            lines = text.split("\n")
            if lines and lines[-1].strip() == footer_pattern:
                text = "\n".join(lines[:-1])

        cleaned.append(
            PDFPage(
                page_number=page.page_number,
                text=text,
                tables=page.tables,
                has_images=page.has_images,
                is_scanned=page.is_scanned,
            )
        )

    return cleaned


def _find_repeated_pattern(lines: list[str], threshold: float = 0.6) -> str:
    """Find a line that appears in more than threshold fraction of pages."""
    if not lines:
        return ""

    from collections import Counter
    counts = Counter(lines)
    for line, count in counts.most_common(3):
        if line and count / len(lines) >= threshold:
            return line
    return ""


def _extract_sections(pages: list[PDFPage]) -> list[PDFSection]:
    """Extract logical sections from PDF pages based on formatting heuristics."""
    sections = []
    current_heading = "Document Content"
    current_content = []
    current_page_start = 1

    for page in pages:
        for line in page.text.split("\n"):
            stripped = line.strip()
            if not stripped:
                continue

            # Heuristic: lines that are short, all caps or title case, might be headings
            is_heading = (
                len(stripped) < 100
                and not stripped.endswith(".")
                and (stripped.isupper() or stripped.istitle())
                and len(stripped.split()) <= 10
            )

            if is_heading and current_content:
                sections.append(
                    PDFSection(
                        heading=current_heading,
                        content="\n".join(current_content),
                        page_start=current_page_start,
                        page_end=page.page_number,
                    )
                )
                current_heading = stripped
                current_content = []
                current_page_start = page.page_number
            else:
                current_content.append(stripped)

    # Last section
    if current_content:
        last_page = pages[-1].page_number if pages else 1
        sections.append(
            PDFSection(
                heading=current_heading,
                content="\n".join(current_content),
                page_start=current_page_start,
                page_end=last_page,
            )
        )

    return sections
