import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import backend.db.session as db_session
from backend.db.models import Document, Chunk, AuditLog, EvaluationResult, User
from sqlalchemy import delete

async def clear_db():
    print("🧹 Cleaning database tables...")
    try:
        await db_session.init_db()
    except Exception as e:
        print(f"⚠️ PostgreSQL connection failed: {e}. Falling back to SQLite...")
        await db_session.switch_to_sqlite()
        await db_session.init_db()
    async with db_session.async_session_factory() as session:
        # Delete chunks, documents, audit logs, evaluations
        await session.execute(delete(Chunk))
        await session.execute(delete(Document))
        await session.execute(delete(AuditLog))
        await session.execute(delete(EvaluationResult))
        await session.commit()
    print("✨ Database tables cleared!")

if __name__ == "__main__":
    asyncio.run(clear_db())
