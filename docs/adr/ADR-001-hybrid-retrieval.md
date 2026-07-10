# ADR-001: Hybrid Retrieval vs Dense-Only Retrieval

**Status:** Accepted  
**Date:** July 2025  
**Author:** Anushka Jain  

## Context

The retrieval pipeline must find relevant document chunks for user queries. Two primary approaches exist: dense-only retrieval (vector similarity search) and hybrid retrieval (combining dense vectors with keyword/BM25 search). Enterprise knowledge contains both natural language content and domain-specific terms, acronyms, and exact phrases that may not be captured well by dense embeddings alone.

## Decision

Implement **hybrid retrieval** combining dense vector search (Qdrant) with keyword search (PostgreSQL full-text search), merged using Reciprocal Rank Fusion (RRF).

## Positive Consequences

1. **Better recall for exact terms** — Keyword search catches acronyms (e.g., "PTO", "Q2"), specific policy numbers, and exact phrases that dense retrieval may miss
2. **Better semantic understanding** — Dense retrieval captures meaning even when exact terms don't match
3. **Proven effectiveness** — Research shows hybrid retrieval consistently outperforms either method alone
4. **Graceful degradation** — If one method fails, the other still provides results
5. **No additional infrastructure** — PostgreSQL FTS leverages existing metadata database

## Negative Consequences

1. **Higher latency** — Two retrieval paths + fusion adds processing time (~100-200ms)
2. **More complexity** — Two indexes to maintain, fusion weights to tune
3. **Index maintenance** — tsvector columns must be kept in sync with content

## Alternatives Considered

1. **Dense-only (Qdrant)** — Simpler but misses exact term matches. Rejected because enterprise queries often contain specific terms.
2. **BM25-only (Elasticsearch)** — Strong for exact matches but poor for semantic similarity. Rejected because users don't always use exact terminology.
3. **Elasticsearch + Qdrant** — Would add Elasticsearch as additional infrastructure. Rejected to minimize operational complexity; PostgreSQL FTS is sufficient for demo-scale.

## Future Review

- Re-evaluate if latency exceeds 500ms for the retrieval phase
- Consider learned sparse retrieval (SPLADE) as a third signal
- Benchmark against ColBERT for potential single-model replacement
