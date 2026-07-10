# ADR-006: Duplicate Detection and Source-Version Resolution

**Status:** Accepted  
**Date:** July 2025  
**Author:** Anushka Jain  

## Context

Enterprise knowledge bases contain duplicate and versioned documents — the same policy may exist as v1 and v2, a document may be stored in both the wiki and as a PDF, or near-duplicate content may appear across departments. Without deduplication and version resolution, retrieval results become noisy with redundant information.

## Decision

Implement multi-level duplicate and version handling:
1. **Exact duplicates:** Content-hash (SHA-256) based deduplication
2. **Near-duplicates:** Text similarity deduplication during retrieval (first-200-char hash)
3. **Version tracking:** `version` and `is_current_version` fields on documents
4. **Canonical documents:** `canonical_document_id` to link versions
5. **Source trust hierarchy:** Official → Approved → Informal → Unverified
6. **Conflict handling:** When sources conflict, state the conflict explicitly

## Positive Consequences

1. **Cleaner retrieval** — Duplicate chunks don't dominate results
2. **Version awareness** — Current versions are preferred over outdated ones
3. **Trust signals** — Official policies rank above informal Slack messages
4. **Transparency** — Conflicts are surfaced rather than silently resolved

## Negative Consequences

1. **Metadata overhead** — Additional fields on every document
2. **Manual version linking** — Canonical document IDs must be set during ingestion
3. **May miss near-duplicates** — Simple hashing won't catch all semantic duplicates

## Alternatives Considered

1. **No deduplication** — Let duplicates exist. Rejected because duplicate chunks waste LLM context tokens.
2. **Semantic deduplication (embedding similarity)** — More accurate but computationally expensive at ingestion time. Considered for future improvement.
3. **Automatic version detection** — Use document titles and dates to infer versions. Partially implemented; full automation deferred.

## Source Trust Hierarchy

When conflicting evidence is found, prefer (in order):
1. Approved official policy (`official`)
2. Official wiki documentation (`approved`)
3. Approved report or spreadsheet (`approved`)
4. Technical documentation (`informal`)
5. Slack discussions (`unverified`)

If conflict remains after trust-level resolution, the system explicitly states the conflict.

## Future Review

- Implement embedding-based near-duplicate detection
- Add automatic version detection from document metadata
- Consider temporal weighting (newer documents score higher)
