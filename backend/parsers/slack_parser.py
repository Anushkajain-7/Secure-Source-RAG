"""
SecureSource RAG — Slack JSON Parser

Parses Slack-style threaded conversation JSON, preserving:
- Channel name
- Parent messages and replies
- Authors and timestamps
- Thread identifiers
- Message threading
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class SlackMessage:
    """A single Slack message."""
    message_id: str
    author: str
    text: str
    timestamp: str
    is_parent: bool = True
    thread_ts: Optional[str] = None
    reactions: list[str] = field(default_factory=list)


@dataclass
class SlackThread:
    """A Slack thread with parent message and replies."""
    thread_id: str
    channel: str
    parent_message: SlackMessage
    replies: list[SlackMessage] = field(default_factory=list)
    full_text: str = ""


@dataclass
class ParsedSlack:
    """Result of parsing a Slack JSON file."""
    channel: str
    threads: list[SlackThread]
    raw_text: str
    metadata: dict
    content_hash: str
    total_messages: int = 0
    errors: list[str] = field(default_factory=list)


def parse_slack(file_path: str | Path, raw_content: str | None = None) -> ParsedSlack:
    """
    Parse a Slack-style JSON file into threaded conversations.

    Expected JSON format:
    {
        "channel": "engineering-incidents",
        "messages": [
            {
                "id": "msg-001",
                "author": "Jane Smith",
                "text": "...",
                "timestamp": "2025-01-15T10:30:00Z",
                "thread_ts": null,
                "replies": [
                    {
                        "id": "msg-002",
                        "author": "John Doe",
                        "text": "...",
                        "timestamp": "2025-01-15T10:35:00Z"
                    }
                ]
            }
        ]
    }
    """
    path = Path(file_path)
    errors = []

    if raw_content is None:
        try:
            raw_content = path.read_text(encoding="utf-8")
        except Exception as e:
            return ParsedSlack(
                channel="unknown",
                threads=[],
                raw_text="",
                metadata={"source_name": path.name},
                content_hash="",
                errors=[f"Failed to read file: {e}"],
            )

    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError as e:
        return ParsedSlack(
            channel="unknown",
            threads=[],
            raw_text=raw_content,
            metadata={"source_name": path.name},
            content_hash=hashlib.sha256(raw_content.encode()).hexdigest(),
            errors=[f"Invalid JSON: {e}"],
        )

    channel = data.get("channel", "unknown")
    messages = data.get("messages", [])

    threads = []
    total_messages = 0

    for msg_data in messages:
        parent = SlackMessage(
            message_id=msg_data.get("id", ""),
            author=msg_data.get("author", "Unknown"),
            text=msg_data.get("text", ""),
            timestamp=msg_data.get("timestamp", ""),
            is_parent=True,
            thread_ts=msg_data.get("thread_ts"),
        )
        total_messages += 1

        replies = []
        for reply_data in msg_data.get("replies", []):
            reply = SlackMessage(
                message_id=reply_data.get("id", ""),
                author=reply_data.get("author", "Unknown"),
                text=reply_data.get("text", ""),
                timestamp=reply_data.get("timestamp", ""),
                is_parent=False,
                thread_ts=msg_data.get("id"),
            )
            replies.append(reply)
            total_messages += 1

        # Build full text representation
        full_text_parts = [
            f"[{parent.author}] ({parent.timestamp}): {parent.text}"
        ]
        for reply in replies:
            full_text_parts.append(
                f"  ↳ [{reply.author}] ({reply.timestamp}): {reply.text}"
            )
        full_text = "\n".join(full_text_parts)

        thread = SlackThread(
            thread_id=parent.message_id,
            channel=channel,
            parent_message=parent,
            replies=replies,
            full_text=full_text,
        )
        threads.append(thread)

    raw_text = "\n\n---\n\n".join(t.full_text for t in threads)
    content_hash = hashlib.sha256(raw_text.encode()).hexdigest()

    return ParsedSlack(
        channel=channel,
        threads=threads,
        raw_text=raw_text,
        metadata={
            "source_name": path.name,
            "channel": channel,
            "total_messages": total_messages,
            "total_threads": len(threads),
        },
        content_hash=content_hash,
        total_messages=total_messages,
        errors=errors,
    )
