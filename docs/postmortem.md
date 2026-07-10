# SecureSource RAG — Postmortem Template

> **Note:** This is a TEMPLATE for a realistic postmortem. No actual production bug occurred. This document demonstrates postmortem writing skills.

---

## Incident: Unauthorized Salary Data Leaked via Cached Retrieval Results

**Date:** `[TEMPLATE — Not a real incident]`  
**Severity:** P1 — Data Security  
**Duration:** ~45 minutes  
**Author:** Anushka Jain  
**Status:** Template (Fictional)  

---

## Impact

- 3 engineering users received salary band information in query responses
- Confidential HR data was included in LLM context for approximately 45 minutes
- No external data exposure (internal system only)
- Affected users notified and audit logs preserved

## Detection

- HR Manager noticed salary data in a colleague's shared screenshot of a query response
- Escalated to engineering via Slack at 14:20 UTC
- Confirmed by audit log review at 14:35 UTC

## Timeline

| Time (UTC) | Event |
|------------|-------|
| 13:30 | Deployment of v1.2.3 with new caching layer for retrieval results |
| 13:35 | Cache warming begins, pre-computing results for common queries |
| 13:40 | Cache stores results for "compensation" query using admin user context |
| 14:00 | Engineering user queries "What is the compensation structure?" |
| 14:00 | Cache returns admin-context results (including salary bands) bypassing ACL filter |
| 14:20 | HR Manager reports seeing salary data in colleague's response |
| 14:35 | Engineering confirms issue via audit logs |
| 14:40 | Cache disabled via feature flag |
| 14:45 | Cache fully cleared |
| 14:50 | Verification: subsequent queries correctly filtered by user ACL |

## Root Cause

The new retrieval caching layer cached query results **after** the full pipeline (including ACL-filtered results) but served cached results to subsequent users **without re-applying their ACL filters**. The cache key was based on the query text only, not on the query text + user permissions.

When the cache was warmed with an admin user's query, the admin-level results (which included restricted documents) were served to all subsequent users asking similar questions.

## Contributing Factors

1. **Cache key design:** Cache key was `hash(query)` instead of `hash(query + user_id + permissions)`
2. **Insufficient testing:** No integration test verified that cached results respected per-user ACLs
3. **Feature flag bypass:** Cache was enabled in production without gradual rollout
4. **No security review:** The caching PR was reviewed for performance but not for security implications

## Fix

1. **Immediate:** Disabled cache via feature flag, cleared all cached entries
2. **Short-term:** Changed cache key to include user_id and permission hash
3. **Medium-term:** Added integration test: "cached results must not leak across users with different permissions"

## Prevention

1. All retrieval layer changes now require security review
2. Cache keys for user-specific data must include permission context
3. Added automated test: same query, two users, different permissions → different results
4. Feature flag rollout policy: security-sensitive features require staged deployment

## Tests Added

- `test_cache_respects_acl`: Verifies cached results are user-specific
- `test_cache_key_includes_permissions`: Verifies cache key contains permission hash
- `test_cross_user_cache_isolation`: Verifies User A's cache doesn't leak to User B

## Lessons Learned

1. **Caching and access control are fundamentally in tension.** Any cache that stores per-user results must include user identity in the cache key. This seems obvious in retrospect but was missed because the caching PR focused on latency, not security.

2. **Security review must be mandatory for retrieval layer changes.** The retrieval pipeline is the security boundary — any change to it can potentially bypass ACL enforcement.

3. **The principle of "filter before context" applies to caches too.** Our architecture correctly filters at retrieval time, but the cache created a second path that bypassed the filter.

## What Would Be Done Differently

1. Include security engineer in PR review for any retrieval/caching changes
2. Write security tests before implementing the feature, not after the incident
3. Design cache with per-user isolation from the start
4. Run the full integration test suite (including ACL tests) against cached code paths
