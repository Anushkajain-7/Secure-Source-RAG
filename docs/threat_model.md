# SecureSource RAG — Threat Model

**Author:** Anushka Jain  
**Date:** July 2025  
**Classification:** Internal  

---

## Scope

This threat model covers the SecureSource RAG application, including the retrieval pipeline, LLM generation, access control, and data storage layers.

---

## Threat Analysis

### T1: Unauthorized Document Retrieval

| Aspect | Detail |
|--------|--------|
| **Threat** | A user retrieves documents they should not have access to |
| **Impact** | HIGH — Confidential data exposure (salary bands, strategy docs) |
| **Likelihood** | MEDIUM — Possible through ACL misconfiguration or bypass |
| **Mitigation** | Three-layer ACL filtering (Qdrant payload, PostgreSQL WHERE, verification gate). Chunk-level inherited ACLs. Admin-only source management. |
| **Residual Risk** | LOW — ACL bypass would require compromise of all three layers |

### T2: Metadata Leakage

| Aspect | Detail |
|--------|--------|
| **Threat** | Unauthorized user learns of restricted documents through titles, filenames, or citation references |
| **Impact** | MEDIUM — Reveals existence of confidential documents |
| **Likelihood** | MEDIUM — LLMs may reference filtered documents in responses |
| **Mitigation** | Unauthorized chunks never enter LLM context. Citation validation removes unauthorized references. Safe refusal doesn't reveal document existence. |
| **Residual Risk** | LOW — System never sees unauthorized content |

### T3: Prompt Injection from Documents

| Aspect | Detail |
|--------|--------|
| **Threat** | Malicious text in a document overrides system instructions |
| **Impact** | HIGH — Could disable security controls, expose data |
| **Likelihood** | MEDIUM — Requires ability to upload documents |
| **Mitigation** | Retrieved content wrapped in data delimiters. System prompt explicitly ignores document instructions. Test document with injection attempt included. |
| **Residual Risk** | MEDIUM — LLMs are inherently vulnerable; defense is probabilistic |

### T4: Data Exfiltration

| Aspect | Detail |
|--------|--------|
| **Threat** | Crafted queries designed to extract and reconstruct full documents |
| **Impact** | HIGH — Complete document content leaked |
| **Likelihood** | LOW — Chunking and summarization make reconstruction difficult |
| **Mitigation** | Chunk-level retrieval (not full document). Rate limiting. Audit logging of all queries. Evidence excerpts rather than full text in responses. |
| **Residual Risk** | LOW — Would require many queries, detectable via audit |

### T5: Malicious File Upload

| Aspect | Detail |
|--------|--------|
| **Threat** | Uploaded file contains malware or exploits parser vulnerabilities |
| **Impact** | HIGH — Server compromise |
| **Likelihood** | LOW — Upload restricted to admin users |
| **Mitigation** | Admin-only upload. File type validation. Sandboxed parsing. Input size limits. |
| **Residual Risk** | LOW — Limited upload surface, admin-only access |

### T6: PII Leakage

| Aspect | Detail |
|--------|--------|
| **Threat** | Personal information exposed through queries or logs |
| **Impact** | HIGH — Privacy violation, regulatory risk |
| **Likelihood** | MEDIUM — Synthetic data minimizes risk but production data would increase it |
| **Mitigation** | Synthetic data only. Structured logging with field redaction. No PII in audit log question fields (truncated). |
| **Residual Risk** | LOW (demo) / MEDIUM (production) |

### T7: Log Leakage

| Aspect | Detail |
|--------|--------|
| **Threat** | Sensitive content exposed through application logs |
| **Impact** | MEDIUM — Internal data visible in log aggregation systems |
| **Likelihood** | MEDIUM — Default logging often captures too much |
| **Mitigation** | Structured logging with explicit field selection. Questions truncated in logs. No raw document content in logs. |
| **Residual Risk** | LOW — Controlled log fields |

### T8: Secret Exposure

| Aspect | Detail |
|--------|--------|
| **Threat** | API keys or credentials committed to source control |
| **Impact** | HIGH — Account compromise |
| **Likelihood** | LOW — .env.example pattern prevents accidental commits |
| **Mitigation** | .env.example with placeholders only. .gitignore for .env. Environment-based configuration. No hardcoded secrets. |
| **Residual Risk** | LOW — Standard secret management |

### T9: Citation Spoofing

| Aspect | Detail |
|--------|--------|
| **Threat** | LLM generates fabricated citations pointing to non-existent pages or rows |
| **Impact** | MEDIUM — User trusts false information |
| **Likelihood** | HIGH — LLMs frequently hallucinate citations |
| **Mitigation** | Citation validation against retrieved chunks. Metadata sourced from chunk records, not LLM output. Verification logged. |
| **Residual Risk** | LOW — Validation catches fabricated citations |

### T10: Cross-User Leakage

| Aspect | Detail |
|--------|--------|
| **Threat** | One user's query results leak into another user's session |
| **Impact** | HIGH — Unauthorized data access |
| **Likelihood** | LOW — Stateless API design minimizes risk |
| **Mitigation** | Stateless requests with per-request ACL filtering. No shared cache of results. Session isolation. |
| **Residual Risk** | LOW — Stateless architecture |

### T11: Denial of Service

| Aspect | Detail |
|--------|--------|
| **Threat** | Excessive queries overwhelm the system |
| **Impact** | MEDIUM — Service degradation |
| **Likelihood** | LOW — Demo system with limited users |
| **Mitigation** | Rate limiting (future). Query length limits. Timeout on LLM calls. Connection pool limits. |
| **Residual Risk** | MEDIUM — No rate limiting implemented yet |

### T12: Outdated Policy Risk

| Aspect | Detail |
|--------|--------|
| **Threat** | User receives advice based on superseded policy |
| **Impact** | MEDIUM — Incorrect decisions based on outdated information |
| **Likelihood** | MEDIUM — Multiple versions of documents exist in dataset |
| **Mitigation** | Version tracking with is_current_version flag. Outdated documents deprioritized. Trust-level hierarchy. Conflicting sources stated explicitly. |
| **Residual Risk** | LOW — Version-aware retrieval |
