"""
SecureSource RAG — Markdown/Wiki Parser

Parses Markdown and Confluence-style wiki pages, preserving:
- Document title
- Heading hierarchy
- Sections and subsections
- Update date
- Metadata from YAML frontmatter (if present)
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class MarkdownSection:
    """A section extracted from a Markdown document."""
    heading: str
    level: int  # 1-6
    content: str
    parent_heading: Optional[str] = None
    subsections: list["MarkdownSection"] = field(default_factory=list)


@dataclass
class ParsedMarkdown:
    """Result of parsing a Markdown file."""
    title: str
    raw_text: str
    sections: list[MarkdownSection]
    metadata: dict
    content_hash: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    errors: list[str] = field(default_factory=list)


def parse_markdown(file_path: str | Path, raw_content: str | None = None) -> ParsedMarkdown:
    """
    Parse a Markdown file into structured sections.

    Args:
        file_path: Path to the Markdown file
        raw_content: Optional pre-loaded content string

    Returns:
        ParsedMarkdown with title, sections, and metadata
    """
    path = Path(file_path)
    errors = []

    if raw_content is None:
        try:
            raw_content = path.read_text(encoding="utf-8")
        except Exception as e:
            return ParsedMarkdown(
                title=path.stem,
                raw_text="",
                sections=[],
                metadata={"source_name": path.name},
                content_hash="",
                errors=[f"Failed to read file: {e}"],
            )

    # Extract frontmatter if present
    metadata, body = _extract_frontmatter(raw_content)
    metadata["source_name"] = path.name

    # Extract title
    title = metadata.get("title", "")
    if not title:
        title = _extract_title(body) or path.stem

    # Parse dates
    created_at = _parse_date(metadata.get("created_at") or metadata.get("date"))
    updated_at = _parse_date(metadata.get("updated_at") or metadata.get("last_updated"))

    # Split into sections
    sections = _split_into_sections(body)

    # Content hash for duplicate detection
    content_hash = hashlib.sha256(raw_content.encode("utf-8")).hexdigest()

    return ParsedMarkdown(
        title=title,
        raw_text=raw_content,
        sections=sections,
        metadata=metadata,
        content_hash=content_hash,
        created_at=created_at,
        updated_at=updated_at,
        errors=errors,
    )


def _extract_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter from Markdown content."""
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    frontmatter_text = parts[1].strip()
    body = parts[2].strip()

    metadata = {}
    for line in frontmatter_text.split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            metadata[key.strip()] = value.strip().strip('"').strip("'")

    return metadata, body


def _parse_date(date_str: str | None) -> datetime | None:
    """Parse a date string into a datetime object."""
    if not date_str:
        return None
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.replace(tzinfo=timezone.utc)
    except Exception:
        try:
            dt = datetime.fromisoformat(date_str)
            if not dt.tzinfo:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return None


def _extract_title(content: str) -> str:
    """Extract the first H1 heading as the title."""
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("# ") and not line.startswith("## "):
            return line[2:].strip()
    return ""


def _split_into_sections(content: str) -> list[MarkdownSection]:
    """Split Markdown content into heading-based sections."""
    sections = []
    current_heading = "Introduction"
    current_level = 0
    current_lines = []
    heading_stack: list[tuple[int, str]] = []  # Stack of (level, heading_text)

    for line in content.split("\n"):
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)

        if heading_match:
            # Save previous section if it has content or isn't the default Introduction
            section_content = "\n".join(current_lines).strip()
            if section_content or current_heading != "Introduction":
                # Find parent heading
                parent = None
                for l, h in reversed(heading_stack):
                    if l < current_level:
                        parent = h
                        break
                sections.append(
                    MarkdownSection(
                        heading=current_heading,
                        level=current_level,
                        content=section_content,
                        parent_heading=parent,
                    )
                )

            # Start new section
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()

            # Pop from stack until we find a higher level (lower level number)
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()

            # Push current to stack
            heading_stack.append((level, heading_text))

            current_heading = heading_text
            current_level = level
            current_lines = []
        else:
            current_lines.append(line)

    # Save the last section
    section_content = "\n".join(current_lines).strip()
    if section_content or current_heading != "Introduction":
        parent = None
        for l, h in reversed(heading_stack):
            if l < current_level:
                parent = h
                break
        sections.append(
            MarkdownSection(
                heading=current_heading,
                level=current_level,
                content=section_content,
                parent_heading=parent,
            )
        )

    return sections
