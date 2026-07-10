"""
SecureSource RAG — OCR Parser

Handles scanned PDFs by detecting insufficient text extraction
and applying Tesseract OCR to extract text from page images.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from backend.parsers.pdf_parser import PDFPage, ParsedPDF


@dataclass
class OCRResult:
    """Result of OCR processing on a single page."""
    page_number: int
    text: str
    confidence: float = 0.0
    method: str = "tesseract"


@dataclass
class ParsedScannedPDF:
    """Result of OCR processing a scanned PDF."""
    title: str
    source_name: str
    pages: list[OCRResult]
    raw_text: str
    content_hash: str
    metadata: dict
    total_pages: int = 0
    avg_confidence: float = 0.0
    errors: list[str] = field(default_factory=list)


def parse_scanned_pdf(
    file_path: str | Path,
    file_bytes: bytes | None = None,
) -> ParsedScannedPDF:
    """
    Process a scanned PDF through OCR.

    1. Opens the PDF
    2. Renders each page to an image
    3. Runs Tesseract OCR on each image
    4. Returns extracted text with confidence scores

    Args:
        file_path: Path to the scanned PDF
        file_bytes: Optional pre-loaded bytes

    Returns:
        ParsedScannedPDF with OCR results
    """
    path = Path(file_path)
    errors = []

    try:
        import fitz  # PyMuPDF
    except ImportError:
        return ParsedScannedPDF(
            title=path.stem,
            source_name=path.name,
            pages=[],
            raw_text="",
            content_hash="",
            metadata={"source_name": path.name},
            errors=["PyMuPDF not installed"],
        )

    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return ParsedScannedPDF(
            title=path.stem,
            source_name=path.name,
            pages=[],
            raw_text="",
            content_hash="",
            metadata={"source_name": path.name},
            errors=["pytesseract or Pillow not installed"],
        )

    # Open PDF
    try:
        if file_bytes:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        else:
            doc = fitz.open(str(path))
    except Exception as e:
        return ParsedScannedPDF(
            title=path.stem,
            source_name=path.name,
            pages=[],
            raw_text="",
            content_hash="",
            metadata={"source_name": path.name},
            errors=[f"Failed to open PDF: {e}"],
        )

    ocr_results = []
    all_text = []
    total_confidence = 0.0

    for page_num in range(len(doc)):
        try:
            page = doc[page_num]

            # Render page to image at 300 DPI
            mat = fitz.Matrix(300 / 72, 300 / 72)
            pix = page.get_pixmap(matrix=mat)

            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Run OCR
            ocr_data = pytesseract.image_to_data(
                img, lang="eng", output_type=pytesseract.Output.DICT
            )

            # Extract text and confidence
            words = []
            confidences = []
            for i, word in enumerate(ocr_data["text"]):
                if word.strip():
                    words.append(word)
                    conf = int(ocr_data["conf"][i])
                    if conf > 0:
                        confidences.append(conf)

            text = " ".join(words)
            avg_conf = sum(confidences) / max(len(confidences), 1)

            ocr_results.append(
                OCRResult(
                    page_number=page_num + 1,
                    text=text,
                    confidence=round(avg_conf, 2),
                )
            )
            all_text.append(text)
            total_confidence += avg_conf

        except Exception as e:
            errors.append(f"OCR failed on page {page_num + 1}: {e}")
            ocr_results.append(
                OCRResult(page_number=page_num + 1, text="", confidence=0.0)
            )

    doc.close()

    raw_text = "\n\n".join(all_text)
    content_hash = hashlib.sha256(raw_text.encode()).hexdigest()
    avg_confidence = total_confidence / max(len(ocr_results), 1)

    return ParsedScannedPDF(
        title=path.stem,
        source_name=path.name,
        pages=ocr_results,
        raw_text=raw_text,
        content_hash=content_hash,
        metadata={
            "source_name": path.name,
            "ocr_method": "tesseract",
            "avg_confidence": round(avg_confidence, 2),
            "total_pages": len(ocr_results),
        },
        total_pages=len(ocr_results),
        avg_confidence=round(avg_confidence, 2),
        errors=errors,
    )
