# SecureSource RAG — Initial Design Document

**Author:** Anushka Jain  
**Date:** July 2025  
**Status:** Approved  

---

## Problem

Enterprise employees spend significant time searching for answers across disconnected knowledge systems (wikis, PDFs, Slack, spreadsheets). When they find information, they cannot verify if it's current, complete, or authorized for their role. Existing "chat with PDF" solutions lack access control, citation verification, and multi-format support needed for real enterprise deployment.

## Users

1. **General Employees** — Need quick answers about company policies and procedures
2. **Engineers** — Need access to technical documentation, incident reports, and architecture decisions
3. **HR Managers** — Need access to HR policies, salary bands, and hiring procedures
4. **Finance Analysts** — Need access to budgets, reports, and reimbursement policies
5. **Administrators** — Need visibility into all documents, audit logs, and system health

## Goals

1. Build a RAG system that enforces access control **before** documents reach the LLM
2. Support 5 enterprise document formats with format-specific parsing and chunking
3. Provide verifiable inline citations for every factual claim
4. Handle document versions, duplicates, and conflicting sources
5. Refuse to answer when evidence is insufficient or unauthorized
6. Evaluate the system with a structured 100-question dataset
7. Maintain comprehensive audit logs for compliance

## Non-Goals

1. Real-time document synchronization with external systems
2. Multi-turn conversational memory
3. Agent-based tool use or autonomous actions
4. Production-grade authentication (OAuth/SAML)
5. Horizontal scaling or multi-region deployment
6. Fine-tuning LLMs on enterprise data

## Main Features

- **Hybrid Retrieval** — Dense vector + keyword search with RRF fusion
- **ACL Enforcement** — Document and chunk-level permissions checked at retrieval time
- **Source-Aware Chunking** — Different strategies for wikis, PDFs, threads, tables
- **Citation Validation** — Every citation verified against retrieved evidence
- **Safe Refusals** — Explicit refusal when evidence is insufficient
- **Prompt Injection Defense** — Retrieved content treated as untrusted data
- **Evaluation Framework** — 100-question dataset with 12+ metrics

## Architecture

Three-tier architecture:
- **Frontend:** Next.js + Tailwind CSS (5 screens)
- **Backend:** FastAPI with modular service design (15+ modules)
- **Data:** PostgreSQL (metadata + FTS) + Qdrant (vectors)

Security is enforced at the retrieval layer, not the UI layer.

## Security Model

1. Document-level ACLs with department, role, and user-level controls
2. Chunk-level ACL inheritance during ingestion
3. Qdrant payload filtering for dense retrieval
4. PostgreSQL WHERE clauses for keyword retrieval
5. Final ACL verification before context construction
6. Citation authorization before response delivery
7. Prompt injection resistance via system prompt hardening

## Success Criteria

- [ ] 5 demo users with distinct access levels
- [ ] 4+ source types parsed and indexed
- [ ] Hybrid retrieval with re-ranking
- [ ] ACL filtering prevents unauthorized access
- [ ] Citations point to actual retrieved evidence
- [ ] Evaluation dashboard shows metrics
- [ ] System runnable within 15 minutes
- [ ] All security tests pass

## Risks

| Risk | Mitigation |
|------|-----------|
| LLM API rate limits | Provider abstraction with fallback |
| OCR quality on scans | Confidence scoring; clean synthetic data |
| Scope too large | Phase-based development; working skinny path first |
| Evaluation validity | Structured dataset with clear expected answers |

## Technology Choices

See [ADR documents](adr/) for detailed decision rationale on each technology choice.
