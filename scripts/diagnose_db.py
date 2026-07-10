import asyncio
import sys
from pathlib import Path
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parent.parent))
import backend.db.session as db_session

async def diagnose():
    await db_session.switch_to_sqlite()
    await db_session.init_db()
    async with db_session.async_session_factory() as session:
        # Check documents table count
        doc_count = await session.execute(text("SELECT COUNT(*) FROM documents"))
        print(f"Total documents: {doc_count.scalar()}")

        # Check chunks table count
        chunk_count = await session.execute(text("SELECT COUNT(*) FROM chunks"))
        print(f"Total chunks: {chunk_count.scalar()}")

        # Print some documents
        docs = await session.execute(text("SELECT document_id, source_name, is_current_version, department, access_level FROM documents LIMIT 5"))
        print("\nDocuments sample:")
        for r in docs:
            print(f"  ID: {r[0]}, Name: {r[1]}, IsCurrent: {r[2]} (type: {type(r[2])}), Dept: {r[3]}, Access: {r[4]}")

        # Check chunks of one document
        chunks = await session.execute(text("SELECT chunk_id, document_id, raw_text FROM chunks LIMIT 2"))
        print("\nChunks sample:")
        for r in chunks:
            print(f"  ChunkID: {r[0]}, DocID: {r[1]}, Text: {r[2][:60]}...")

if __name__ == "__main__":
    asyncio.run(diagnose())
