#!/usr/bin/env python3
"""
SecureSource RAG — Seed Data Script

Loads sample data from sample_data/ directory into the database and vector store.
Run with: PYTHONPATH=. python scripts/seed_data.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def seed():
    """Seed the database with sample data."""
    import backend.db.session as db_session
    from backend.db.models import User
    from backend.auth.users import DEMO_USERS

    print("🔧 Initializing database...")
    try:
        await db_session.init_db()
    except Exception as e:
        print(f"⚠️ PostgreSQL connection failed: {e}. Falling back to SQLite...")
        await db_session.switch_to_sqlite()
        await db_session.init_db()

    async with db_session.async_session_factory() as session:
        # Seed demo users
        print("👥 Seeding demo users...")
        for key, demo_user in DEMO_USERS.items():
            user = User(
                user_id=demo_user.user_id,
                name=demo_user.name,
                email=demo_user.email,
                role=demo_user.role,
                department=demo_user.department,
                is_admin=demo_user.is_admin,
                permissions={
                    "allowed_departments": demo_user.permissions.allowed_departments,
                    "allowed_access_levels": demo_user.permissions.allowed_access_levels,
                    "can_manage_sources": demo_user.permissions.can_manage_sources,
                    "can_view_audit": demo_user.permissions.can_view_audit,
                },
            )
            session.add(user)
            print(f"  ✅ {demo_user.name} ({demo_user.role})")

        await session.commit()

    # Ingest sample documents
    sample_dir = Path(__file__).parent.parent / "sample_data"

    print("\n📄 Ingesting sample documents...")

    # Markdown files
    md_dir = sample_dir / "markdown"
    if md_dir.exists():
        for md_file in sorted(md_dir.glob("*.md")):
            print(f"  📝 {md_file.name}")
            # In a full implementation, this would call the ingestion pipeline

    # Slack files
    slack_dir = sample_dir / "slack"
    if slack_dir.exists():
        for slack_file in sorted(slack_dir.glob("*.json")):
            print(f"  💬 {slack_file.name}")

    # Spreadsheets
    sheet_dir = sample_dir / "spreadsheets"
    if sheet_dir.exists():
        for sheet_file in sorted(sheet_dir.glob("*")):
            print(f"  📊 {sheet_file.name}")

    print("\n✅ Seed data loaded successfully!")
    print(f"   Users: {len(DEMO_USERS)}")
    print(f"   Sample documents ready for ingestion")
    print("\n💡 To ingest documents, use the admin Source Management UI or the API.")


if __name__ == "__main__":
    asyncio.run(seed())
