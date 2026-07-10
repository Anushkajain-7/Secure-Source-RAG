"""
SecureSource RAG — Spreadsheet Parser

Parses Excel (.xlsx) and CSV files, preserving:
- File name and sheet names
- Column names
- Row numbers and ranges
- Table titles
- Multi-sheet support
"""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass, field
from io import BytesIO, StringIO
from pathlib import Path
from typing import Optional


@dataclass
class SpreadsheetRow:
    """A single row from a spreadsheet."""
    row_number: int
    data: dict[str, str]  # column_name -> value


@dataclass
class SpreadsheetSheet:
    """A sheet/tab from a spreadsheet."""
    sheet_name: str
    columns: list[str]
    rows: list[SpreadsheetRow]
    title: Optional[str] = None
    text_representation: str = ""


@dataclass
class ParsedSpreadsheet:
    """Result of parsing a spreadsheet file."""
    source_name: str
    sheets: list[SpreadsheetSheet]
    raw_text: str
    metadata: dict
    content_hash: str
    total_rows: int = 0
    total_sheets: int = 0
    errors: list[str] = field(default_factory=list)


def parse_spreadsheet(
    file_path: str | Path,
    file_bytes: bytes | None = None,
) -> ParsedSpreadsheet:
    """
    Parse an Excel or CSV file.

    Args:
        file_path: Path to the spreadsheet file
        file_bytes: Optional pre-loaded bytes

    Returns:
        ParsedSpreadsheet with sheets, rows, and metadata
    """
    path = Path(file_path)
    errors = []
    suffix = path.suffix.lower()

    if suffix in (".xlsx", ".xls"):
        return _parse_excel(path, file_bytes, errors)
    elif suffix == ".csv":
        return _parse_csv(path, file_bytes, errors)
    else:
        return ParsedSpreadsheet(
            source_name=path.name,
            sheets=[],
            raw_text="",
            metadata={"source_name": path.name},
            content_hash="",
            errors=[f"Unsupported file type: {suffix}"],
        )


def _parse_excel(
    path: Path,
    file_bytes: bytes | None,
    errors: list[str],
) -> ParsedSpreadsheet:
    """Parse an Excel file using pandas + openpyxl."""
    try:
        import pandas as pd
    except ImportError:
        return ParsedSpreadsheet(
            source_name=path.name,
            sheets=[],
            raw_text="",
            metadata={"source_name": path.name},
            content_hash="",
            errors=["pandas not installed"],
        )

    try:
        if file_bytes:
            excel_file = pd.ExcelFile(BytesIO(file_bytes), engine="openpyxl")
        else:
            excel_file = pd.ExcelFile(str(path), engine="openpyxl")
    except Exception as e:
        return ParsedSpreadsheet(
            source_name=path.name,
            sheets=[],
            raw_text="",
            metadata={"source_name": path.name},
            content_hash="",
            errors=[f"Failed to open Excel file: {e}"],
        )

    sheets = []
    total_rows = 0
    all_text_parts = []

    for sheet_name in excel_file.sheet_names:
        try:
            df = excel_file.parse(sheet_name)
            df = df.fillna("")

            columns = [str(c) for c in df.columns]
            rows = []

            for idx, row in df.iterrows():
                row_data = {col: str(row[col]) for col in columns}
                rows.append(SpreadsheetRow(row_number=int(idx) + 2, data=row_data))  # +2 for header

            total_rows += len(rows)

            # Build text representation
            text_parts = [f"Sheet: {sheet_name}"]
            text_parts.append(f"Columns: {', '.join(columns)}")
            text_parts.append("")

            for row in rows:
                row_text = " | ".join(f"{k}: {v}" for k, v in row.data.items() if v)
                if row_text:
                    text_parts.append(f"Row {row.row_number}: {row_text}")

            text_repr = "\n".join(text_parts)

            sheet = SpreadsheetSheet(
                sheet_name=sheet_name,
                columns=columns,
                rows=rows,
                text_representation=text_repr,
            )
            sheets.append(sheet)
            all_text_parts.append(text_repr)

        except Exception as e:
            errors.append(f"Error parsing sheet '{sheet_name}': {e}")

    raw_text = "\n\n---\n\n".join(all_text_parts)
    content_hash = hashlib.sha256(raw_text.encode()).hexdigest()

    return ParsedSpreadsheet(
        source_name=path.name,
        sheets=sheets,
        raw_text=raw_text,
        metadata={
            "source_name": path.name,
            "total_sheets": len(sheets),
            "sheet_names": [s.sheet_name for s in sheets],
            "total_rows": total_rows,
        },
        content_hash=content_hash,
        total_rows=total_rows,
        total_sheets=len(sheets),
        errors=errors,
    )


def _parse_csv(
    path: Path,
    file_bytes: bytes | None,
    errors: list[str],
) -> ParsedSpreadsheet:
    """Parse a CSV file."""
    try:
        if file_bytes:
            content = file_bytes.decode("utf-8")
        else:
            content = path.read_text(encoding="utf-8")
    except Exception as e:
        return ParsedSpreadsheet(
            source_name=path.name,
            sheets=[],
            raw_text="",
            metadata={"source_name": path.name},
            content_hash="",
            errors=[f"Failed to read CSV: {e}"],
        )

    reader = csv.DictReader(StringIO(content))
    columns = reader.fieldnames or []
    rows = []

    for idx, row_data in enumerate(reader):
        rows.append(
            SpreadsheetRow(
                row_number=idx + 2,
                data={str(k): str(v) for k, v in row_data.items()},
            )
        )

    # Build text representation
    text_parts = [f"File: {path.name}"]
    text_parts.append(f"Columns: {', '.join(columns)}")
    for row in rows:
        row_text = " | ".join(f"{k}: {v}" for k, v in row.data.items() if v)
        if row_text:
            text_parts.append(f"Row {row.row_number}: {row_text}")

    text_repr = "\n".join(text_parts)
    content_hash = hashlib.sha256(content.encode()).hexdigest()

    sheet = SpreadsheetSheet(
        sheet_name="Sheet1",
        columns=list(columns),
        rows=rows,
        text_representation=text_repr,
    )

    return ParsedSpreadsheet(
        source_name=path.name,
        sheets=[sheet],
        raw_text=text_repr,
        metadata={
            "source_name": path.name,
            "total_rows": len(rows),
            "columns": list(columns),
        },
        content_hash=content_hash,
        total_rows=len(rows),
        total_sheets=1,
        errors=errors,
    )
