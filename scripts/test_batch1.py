import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import backend.db.session as db_session
from backend.auth.users import DEMO_USERS, DemoUser, UserPermissions, build_acl_filter
from backend.retrieval.pipeline import retrieve_and_rank

async def run_test_queries():
    print("🧪 Running Batch 1 Verification Queries...")
    
    # Initialize DB engine connection to SQLite fallback
    await db_session.switch_to_sqlite()
    await db_session.init_db()

    async with db_session.async_session_factory() as session:
        # Define users to test
        aarav = DEMO_USERS["aarav"]      # General Employee
        anushka = DEMO_USERS["anushka"]  # Software Engineer (does NOT have HR/Apollo access, but engineering)
        admin = DEMO_USERS["admin"]      # Admin (full access)

        # We need to add "apollo-devs" group to anushka to test her accessing Apollo specs, or keep it clean
        # Let's test with Aarav vs Anushka vs Admin
        
        # Test Case 1: Carry-over policy (Version Resolution Test)
        # Should return v2 (5 days), NOT v1 (10 days).
        q1 = "What is the annual leave carry-over policy?"
        print(f"\n❓ Question 1: '{q1}' (User: Aarav)")
        aarav_acl = build_acl_filter(aarav)
        res1 = await retrieve_and_rank(q1, aarav_acl, aarav, session)
        print(f"   Results retrieved: {len(res1)}")
        for i, chunk in enumerate(res1[:2]):
            print(f"   [{i+1}] Title: {chunk['source_title']} (v{chunk.get('version', '?')})")
            print(f"       Text: {chunk['raw_text'][:120]}...")
            
        # Test Case 2a: Minimum password length for Aarav (Blocked - general employee)
        q2 = "password requirements"
        print(f"\n❓ Question 2a: '{q2}' (User: Aarav - Blocked)")
        res2a = await retrieve_and_rank(q2, aarav_acl, aarav, session)
        print(f"   Results retrieved: {len(res2a)}")
        for chunk in res2a:
            print(f"   ❌ ERROR: Aarav retrieved: {chunk['source_title']}")
            
        # Test Case 2b: Minimum password length for Anushka (Allowed - Software Engineer)
        print(f"\n❓ Question 2b: '{q2}' (User: Anushka - Allowed)")
        anushka_acl = build_acl_filter(anushka)
        res2b = await retrieve_and_rank(q2, anushka_acl, anushka, session)
        print(f"   Results retrieved: {len(res2b)}")
        for i, chunk in enumerate(res2b[:2]):
            print(f"   [{i+1}] Title: {chunk['source_title']}")
            print(f"       Text: {chunk['raw_text'][:120]}...")

        # Test Case 3: Project Apollo database (Restricted Access Test)
        q3 = "What database does Project Apollo use?"
        
        # 3a. Test with Aarav (General Employee - should be blocked)
        print(f"\n❓ Question 3a: '{q3}' (User: Aarav - Blocked)")
        res3a = await retrieve_and_rank(q3, aarav_acl, aarav, session)
        print(f"   Results retrieved: {len(res3a)}")
        for chunk in res3a:
            print(f"   ❌ ERROR: Aarav retrieved: {chunk['source_title']}")

        # 3b. Test with Anushka (Software Engineer - should be blocked because she is not in apollo-devs role/group)
        print(f"\n❓ Question 3c: '{q3}' (User: Anushka - Blocked)")
        res3c = await retrieve_and_rank(q3, anushka_acl, anushka, session)
        print(f"   Results retrieved: {len(res3c)}")
        for chunk in res3c:
            print(f"   ❌ ERROR: Anushka retrieved: {chunk['source_title']}")

        # 3c. Test with Admin (Admin - should be allowed)
        print(f"\n❓ Question 3b: '{q3}' (User: Admin - Allowed)")
        admin_acl = build_acl_filter(admin)
        res3b = await retrieve_and_rank(q3, admin_acl, admin, session)
        print(f"   Results retrieved: {len(res3b)}")
        for i, chunk in enumerate(res3b[:2]):
            print(f"   [{i+1}] Title: {chunk['source_title']}")
            print(f"       Text: {chunk['raw_text'][:120]}...")

if __name__ == "__main__":
    asyncio.run(run_test_queries())
