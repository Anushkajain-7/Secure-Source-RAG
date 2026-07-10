import asyncio
import io
import os
import sys
import uuid
from pathlib import Path
import yaml  # in case we want to parse yaml properly, or we can use our manual split parser

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import backend.db.session as db_session
from fastapi import UploadFile
from backend.db.models import Document, Chunk, User
from backend.ingestion.orchestrator import ingest_file
from sqlalchemy import select, delete

# Simple frontmatter parser
def parse_frontmatter(content: str) -> tuple[dict, bytes]:
    if not content.startswith("---"):
        return {}, content.encode("utf-8")
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content.encode("utf-8")
    
    frontmatter_text = parts[1].strip()
    body = parts[2].strip()
    
    metadata = {}
    for line in frontmatter_text.split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            val = value.strip().strip('"').strip("'")
            # Parse simple lists like ['HR Manager', 'Administrator']
            if val.startswith("[") and val.endswith("]"):
                items = [item.strip().strip("'").strip('"') for item in val[1:-1].split(",") if item.strip()]
                metadata[key.strip()] = items
            else:
                metadata[key.strip()] = val
                
    return metadata, body.encode("utf-8")

async def ingest_directory(directory_path: str, source_type: str):
    print(f"\n📂 Ingesting {source_type} files from: {directory_path}...")
    dir_path = Path(directory_path)
    if not dir_path.exists():
        print(f"⚠️ Directory {directory_path} does not exist. Skipping.")
        return

    # Initialize db
    try:
        await db_session.init_db()
    except Exception as e:
        print(f"⚠️ PostgreSQL connection failed: {e}. Falling back to SQLite...")
        await db_session.switch_to_sqlite()
        await db_session.init_db()

    async with db_session.async_session_factory() as session:
        for filepath in sorted(dir_path.glob("*")):
            # Skip hidden files
            if filepath.name.startswith("."):
                continue
                
            # Filter files by type extension
            if source_type == "markdown" and not filepath.suffix == ".md":
                continue
            if source_type == "slack" and not filepath.suffix == ".json":
                continue
            if source_type in ("spreadsheet", "csv") and filepath.suffix not in (".csv", ".xlsx", ".xls"):
                continue
            if source_type == "pdf" and filepath.suffix != ".pdf":
                continue
            if source_type == "scanned_pdf" and filepath.suffix != ".pdf":
                continue

            print(f"📄 Processing: {filepath.name}...")
            
            # Read content
            with open(filepath, "rb") as f:
                raw_bytes = f.read()

            # Default metadata values
            title = filepath.stem
            department = "general"
            access_level = "public"
            source_trust_level = "official"
            allowed_roles = []
            allowed_users = []
            version = 1
            is_current_version = True
            canonical_doc_id = None
            description = ""
            expected_eval = ""

            # Check for JSON sidecar metadata file
            sidecar_path = filepath.with_suffix(filepath.suffix + ".json")
            if not sidecar_path.exists():
                sidecar_path = filepath.parent / f"{filepath.stem}.metadata.json"

            if sidecar_path.exists():
                try:
                    import json
                    with open(sidecar_path, "r", encoding="utf-8") as sf:
                        meta = json.load(sf)
                    title = meta.get("title", title)
                    department = meta.get("department", department)
                    access_level = meta.get("access_level", access_level)
                    source_trust_level = meta.get("source_trust_level", source_trust_level)
                    allowed_roles = meta.get("allowed_roles", allowed_roles)
                    allowed_users = meta.get("allowed_users", allowed_users)
                    version = int(meta.get("version", version))
                    is_current_version = str(meta.get("is_current_version", "true")).lower() == "true"
                    description = meta.get("description", description)
                    expected_eval = meta.get("expected_evaluation_categories", expected_eval)
                    if "canonical_document_id" in meta:
                        c_id = meta["canonical_document_id"]
                        try:
                            canonical_doc_id = uuid.UUID(c_id)
                        except ValueError:
                            canonical_doc_id = uuid.uuid5(uuid.NAMESPACE_DNS, c_id)
                except Exception as me:
                    print(f"  ⚠️ Error parsing sidecar metadata for {filepath.name}: {me}")

            # If markdown, extract frontmatter
            if source_type == "markdown":
                try:
                    text_content = raw_bytes.decode("utf-8")
                    frontmatter, body = parse_frontmatter(text_content)
                    
                    title = frontmatter.get("title", title)
                    department = frontmatter.get("department", department)
                    access_level = frontmatter.get("access_level", access_level)
                    source_trust_level = frontmatter.get("source_trust_level", source_trust_level)
                    
                    roles_raw = frontmatter.get("allowed_roles", [])
                    if isinstance(roles_raw, list):
                        allowed_roles = roles_raw
                    else:
                        allowed_roles = [r.strip() for r in str(roles_raw).split(",") if r.strip()]
                        
                    users_raw = frontmatter.get("allowed_users", [])
                    if isinstance(users_raw, list):
                        allowed_users = users_raw
                    else:
                        allowed_users = [u.strip() for u in str(users_raw).split(",") if u.strip()]
                        
                    version = int(frontmatter.get("version", 1))
                    is_current_version = str(frontmatter.get("is_current_version", "true")).lower() == "true"
                    description = frontmatter.get("description", "")
                    expected_eval = frontmatter.get("expected_evaluation_categories", "")
                    
                    if "canonical_document_id" in frontmatter:
                        c_id = frontmatter["canonical_document_id"]
                        try:
                            canonical_doc_id = uuid.UUID(c_id)
                        except ValueError:
                            canonical_doc_id = uuid.uuid5(uuid.NAMESPACE_DNS, c_id)
                            
                    # We pass the body bytes to the parser
                    raw_bytes = body
                except Exception as e:
                    print(f"  ⚠️ Error parsing frontmatter for {filepath.name}: {e}. Ingesting as plain markdown.")

            # Construct fastapi-like UploadFile
            upload_file = UploadFile(
                filename=filepath.name,
                file=io.BytesIO(raw_bytes),
                size=len(raw_bytes)
            )

            # Ingest
            res = await ingest_file(
                file=upload_file,
                source_type=source_type,
                department=department,
                access_level=access_level,
                source_trust_level=source_trust_level,
                allowed_roles=allowed_roles,
                allowed_users=allowed_users,
                title=title,
                db=session
            )

            if res.status == "completed":
                print(f"  ✅ Ingested successfully. Chunks created: {res.chunks_created}. ID: {res.document_id}")
                
                # Fetch the document object to update the custom fields (version, is_current_version, canonical_doc_id)
                doc_uuid = uuid.UUID(res.document_id)
                doc = await session.get(Document, doc_uuid)
                if doc:
                    doc.version = version
                    doc.is_current_version = is_current_version
                    if canonical_doc_id:
                        doc.canonical_document_id = canonical_doc_id
                    # Save extra metadata
                    doc.metadata_ = {
                        **(doc.metadata_ or {}),
                        "description": description,
                        "expected_evaluation_categories": expected_eval
                    }
                    session.add(doc)
                    
                    # Update all chunks for this doc to have the same ACL permissions
                    await session.flush()
            else:
                print(f"  ❌ Ingestion failed: {res.errors}")

        await session.commit()
    print("✨ Batch ingestion run complete!")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python run_ingestion.py <directory_path> <source_type>")
        sys.exit(1)
    
    dir_path = sys.argv[1]
    src_type = sys.argv[2]
    
    asyncio.run(ingest_directory(dir_path, src_type))
