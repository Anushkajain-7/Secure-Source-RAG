"""
SecureSource RAG — Ingestion Orchestrator

Coordinates the full ingestion pipeline:
1. Detect source type
2. Parse with appropriate parser
3. Chunk with source-aware strategy
4. Compute embeddings
5. Index into Qdrant + PostgreSQL
6. Create audit trail
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Optional

import structlog
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas import IngestionStatusResponse
from backend.config import get_settings
from backend.db.models import (
    AccessLevel,
    Chunk,
    Department,
    Document,
    IngestionStatus,
    SourceTrustLevel,
    SourceType,
)

settings = get_settings()
logger = structlog.get_logger()


async def ingest_file(
    file: UploadFile,
    source_type: str,
    department: str,
    access_level: str,
    source_trust_level: str,
    allowed_roles: list[str],
    title: str,
    db: AsyncSession,
    allowed_users: list[str] | None = None,
) -> IngestionStatusResponse:
    """
    Full ingestion pipeline for a single file.
    """
    errors = []
    file_bytes = await file.read()
    filename = file.filename or "unknown"

    logger.info("ingestion_start", filename=filename, source_type=source_type)

    # Create document record
    doc = Document(
        source_type=SourceType(source_type),
        source_name=filename,
        source_title=title,
        department=Department(department),
        allowed_roles=allowed_roles or [],
        allowed_users=allowed_users or [],
        access_level=AccessLevel(access_level),
        source_trust_level=SourceTrustLevel(source_trust_level),
        ingestion_status=IngestionStatus.PROCESSING,
        parser_name=f"{source_type}_parser",
    )
    db.add(doc)
    await db.flush()  # Get the document_id

    try:
        # Parse
        parsed, chunks_data = _parse_and_chunk(
            source_type=source_type,
            filename=filename,
            file_bytes=file_bytes,
        )

        if not chunks_data:
            doc.ingestion_status = IngestionStatus.FAILED
            errors.append("No chunks extracted from document")
            return IngestionStatusResponse(
                document_id=str(doc.document_id),
                status="failed",
                chunks_created=0,
                errors=errors,
                parser_name=doc.parser_name,
            )

        # Set content hash
        doc.content_hash = parsed.get("content_hash", "")

        # Create chunk records with inherited ACLs
        chunks_created = 0
        for chunk_data in chunks_data:
            chunk = Chunk(
                document_id=doc.document_id,
                chunk_index=chunk_data.chunk_index,
                raw_text=chunk_data.raw_text,
                cleaned_text=chunk_data.cleaned_text,
                content_hash=chunk_data.content_hash,
                page_number=chunk_data.page_number,
                section_heading=chunk_data.section_heading,
                slack_channel=chunk_data.slack_channel,
                thread_id=chunk_data.thread_id,
                sheet_name=chunk_data.sheet_name,
                row_start=chunk_data.row_start,
                row_end=chunk_data.row_end,
                # Inherit ACLs from parent document
                department=doc.department,
                allowed_roles=doc.allowed_roles,
                allowed_users=doc.allowed_users,
                access_level=doc.access_level,
                source_type=doc.source_type,
                source_trust_level=doc.source_trust_level,
                metadata_=chunk_data.metadata,
            )
            db.add(chunk)
            chunks_created += 1

        # Update document status
        doc.ingestion_status = IngestionStatus.COMPLETED

        await db.flush()

        # Index into Qdrant (async, best-effort)
        try:
            await _index_to_qdrant(doc, chunks_data)
        except Exception as e:
            errors.append(f"Qdrant indexing error: {e}")
            logger.warning("qdrant_indexing_error", error=str(e))

        logger.info(
            "ingestion_complete",
            filename=filename,
            chunks=chunks_created,
        )

        return IngestionStatusResponse(
            document_id=str(doc.document_id),
            status="completed",
            chunks_created=chunks_created,
            errors=errors,
            parser_name=doc.parser_name,
        )

    except Exception as e:
        doc.ingestion_status = IngestionStatus.FAILED
        errors.append(str(e))
        logger.error("ingestion_failed", filename=filename, error=str(e))

        return IngestionStatusResponse(
            document_id=str(doc.document_id),
            status="failed",
            chunks_created=0,
            errors=errors,
            parser_name=doc.parser_name,
        )


def _parse_and_chunk(
    source_type: str,
    filename: str,
    file_bytes: bytes,
) -> tuple[dict, list]:
    """Parse a file and chunk it based on source type."""
    from backend.chunking.chunker import (
        chunk_markdown,
        chunk_pdf,
        chunk_slack,
        chunk_spreadsheet,
    )

    if source_type == "markdown":
        from backend.parsers.markdown_parser import parse_markdown
        parsed = parse_markdown(filename, raw_content=file_bytes.decode("utf-8"))
        chunks = chunk_markdown(parsed)
        return {"content_hash": parsed.content_hash}, chunks

    elif source_type in ("pdf", "scanned_pdf"):
        from backend.parsers.pdf_parser import parse_pdf
        parsed = parse_pdf(filename, file_bytes=file_bytes)

        if parsed.needs_ocr or source_type == "scanned_pdf":
            from backend.parsers.ocr_parser import parse_scanned_pdf
            ocr_result = parse_scanned_pdf(filename, file_bytes=file_bytes)
            # Create simple chunks from OCR pages
            from backend.chunking.chunker import ChunkData
            chunks = []
            for i, page in enumerate(ocr_result.pages):
                if page.text.strip():
                    chunks.append(ChunkData(
                        chunk_index=i,
                        raw_text=page.text,
                        cleaned_text=page.text.strip(),
                        content_hash=hashlib.sha256(page.text.encode()).hexdigest(),
                        page_number=page.page_number,
                        metadata={"ocr_confidence": page.confidence},
                    ))
            return {"content_hash": ocr_result.content_hash}, chunks
        else:
            chunks = chunk_pdf(parsed)
            return {"content_hash": parsed.content_hash}, chunks

    elif source_type == "slack":
        from backend.parsers.slack_parser import parse_slack
        parsed = parse_slack(filename, raw_content=file_bytes.decode("utf-8"))
        chunks = chunk_slack(parsed)
        return {"content_hash": parsed.content_hash}, chunks

    elif source_type in ("spreadsheet", "csv"):
        from backend.parsers.spreadsheet_parser import parse_spreadsheet
        parsed = parse_spreadsheet(filename, file_bytes=file_bytes)
        chunks = chunk_spreadsheet(parsed)
        return {"content_hash": parsed.content_hash}, chunks

    else:
        raise ValueError(f"Unsupported source type: {source_type}")


async def _index_to_qdrant(doc: Document, chunks_data: list) -> None:
    """Index chunks into Qdrant with embeddings and ACL payloads."""
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, PointStruct, VectorParams
        from sentence_transformers import SentenceTransformer

        client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        model = SentenceTransformer(settings.embedding_model)

        # Ensure collection exists
        collections = [c.name for c in client.get_collections().collections]
        if settings.qdrant_collection not in collections:
            client.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=VectorParams(
                    size=settings.embedding_dimension,
                    distance=Distance.COSINE,
                ),
            )

        # Compute embeddings
        texts = [c.cleaned_text for c in chunks_data]
        embeddings = model.encode(texts, normalize_embeddings=True)

        # Create points
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks_data, embeddings)):
            point_id = str(uuid.uuid4())
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding.tolist(),
                    payload={
                        "chunk_id": point_id,
                        "document_id": str(doc.document_id),
                        "raw_text": chunk.raw_text,
                        "cleaned_text": chunk.cleaned_text,
                        "source_type": doc.source_type.value,
                        "source_name": doc.source_name,
                        "source_title": doc.source_title,
                        "department": doc.department.value,
                        "access_level": doc.access_level.value,
                        "allowed_roles": doc.allowed_roles,
                        "allowed_users": doc.allowed_users,
                        "source_trust_level": doc.source_trust_level.value,
                        "page_number": chunk.page_number,
                        "section_heading": chunk.section_heading,
                        "slack_channel": chunk.slack_channel,
                        "thread_id": chunk.thread_id,
                        "sheet_name": chunk.sheet_name,
                        "row_start": chunk.row_start,
                        "row_end": chunk.row_end,
                    },
                )
            )

        # Upsert in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            client.upsert(
                collection_name=settings.qdrant_collection,
                points=batch,
            )

        logger.info(
            "qdrant_indexed",
            document_id=str(doc.document_id),
            points=len(points),
        )

    except Exception as e:
        logger.error("qdrant_index_error", error=str(e))
        raise
