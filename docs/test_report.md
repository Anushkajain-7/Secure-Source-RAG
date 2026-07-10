# SecureSource RAG — Test Report

**Author:** Anushka Jain  
**Date:** July 2025  
**Status:** In Progress  

---

## Test Strategy

### Approach
- **Unit tests:** Test individual components in isolation (parsers, chunking, ACLs, citations)
- **Integration tests:** Test full pipeline paths (authorized retrieval, unauthorized refusal, citation generation)
- **Security tests:** Verify ACL enforcement, prompt injection resistance, metadata leakage prevention
- **CI:** GitHub Actions runs all tests on every push

### Test Framework
- Backend: pytest + pytest-asyncio
- Frontend: Jest (planned)
- Coverage target: 80% for core security modules

---

## Unit Tests

| Test | Module | Status | Description |
|------|--------|--------|-------------|
| test_acl_inheritance | auth | `[PENDING]` | Chunks inherit parent document ACLs |
| test_permission_filter | auth | `[PENDING]` | ACL filter correctly built per user role |
| test_admin_access_all | auth | `[PENDING]` | Admin user bypasses ACL restrictions |
| test_general_user_restricted | auth | `[PENDING]` | General user cannot access restricted docs |
| test_citation_format_pdf | citations | `[PENDING]` | PDF citations include page and section |
| test_citation_format_slack | citations | `[PENDING]` | Slack citations include channel and thread |
| test_citation_format_sheet | citations | `[PENDING]` | Spreadsheet citations include sheet and rows |
| test_citation_authorization | citations | `[PENDING]` | Unauthorized citations are rejected |
| test_markdown_heading_preservation | parsers | `[PENDING]` | Markdown sections preserve heading hierarchy |
| test_pdf_page_preservation | parsers | `[PENDING]` | PDF chunks maintain page numbers |
| test_slack_thread_grouping | parsers | `[PENDING]` | Slack threads keep parent + replies together |
| test_spreadsheet_row_metadata | parsers | `[PENDING]` | Spreadsheet chunks include row ranges |
| test_duplicate_detection | ingestion | `[PENDING]` | Content hash detects exact duplicates |
| test_prompt_injection_filter | security | `[PENDING]` | Injection text does not override system prompt |
| test_refusal_logic | generation | `[PENDING]` | Empty retrieval produces safe refusal |

## Integration Tests

| Test | Status | Description |
|------|--------|-------------|
| Authorized user retrieves allowed doc | `[PENDING]` | Engineer queries engineering doc → success |
| Unauthorized user blocked from restricted doc | `[PENDING]` | General user queries salary bands → refusal |
| Restricted chunks excluded from LLM context | `[PENDING]` | Verify context contains only authorized chunks |
| Answer contains valid citation | `[PENDING]` | Generated answer includes [Source N] references |
| Unsupported question → refusal | `[PENDING]` | Question with no evidence → safe refusal |
| Scanned PDF processed via OCR | `[PENDING]` | OCR produces readable text from scan |
| Spreadsheet cites correct sheet/rows | `[PENDING]` | Budget query → correct sheet and row citation |
| Malicious source ignored | `[PENDING]` | Prompt injection doc doesn't override behavior |

## Security Tests

| Test | Status | Description |
|------|--------|-------------|
| ACL enforcement at Qdrant level | `[PENDING]` | Payload filters applied during search |
| ACL enforcement at PostgreSQL level | `[PENDING]` | WHERE clauses filter unauthorized chunks |
| Metadata leakage prevention | `[PENDING]` | Restricted doc titles not in response |
| Safe refusal wording | `[PENDING]` | Refusal doesn't reveal document existence |
| Prompt injection resistance | `[PENDING]` | Malicious doc text ignored by LLM |

## CI Status

**GitHub Actions:** `[PLACEHOLDER — CI badge/link]`

## Results Summary

| Category | Total | Passed | Failed | Pending |
|----------|-------|--------|--------|---------|
| Unit | 15 | 0 | 0 | 15 |
| Integration | 8 | 0 | 0 | 8 |
| Security | 5 | 0 | 0 | 5 |
| **Total** | **28** | **0** | **0** | **28** |

> **Note:** Tests have been defined but not yet executed. Results will be updated after test implementation and execution.

## Known Limitations

- Frontend tests not yet implemented
- No load/performance testing
- OCR tests require Tesseract installation
- Integration tests require running PostgreSQL and Qdrant

## Untested Areas

- WebSocket/streaming responses (not implemented)
- Concurrent user access patterns
- Large document ingestion (>1000 docs)
- Browser compatibility testing
