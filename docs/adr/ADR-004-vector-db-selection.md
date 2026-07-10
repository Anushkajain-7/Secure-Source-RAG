# ADR-004: Vector Database, Keyword Index, and Reranker Selection

**Status:** Accepted  
**Date:** July 2025  
**Author:** Anushka Jain  

## Context

The retrieval pipeline requires three components: a vector database for dense retrieval, a keyword index for BM25-style retrieval, and a cross-encoder for re-ranking. Multiple options exist for each, with trade-offs in performance, features, operational complexity, and ACL support.

## Decision

- **Vector Database:** Qdrant
- **Keyword Index:** PostgreSQL Full-Text Search (tsvector/tsquery)
- **Reranker:** cross-encoder/ms-marco-MiniLM-L-6-v2

## Positive Consequences

### Qdrant
1. **Native payload filtering** — Can filter by ACL metadata during search, not just after
2. **Lightweight** — Single Docker container, minimal resource usage
3. **Good Python client** — Clean API, well-documented
4. **Scalar quantization** — Can compress vectors for larger datasets

### PostgreSQL FTS
1. **No additional infrastructure** — Reuses the metadata database
2. **Transactional consistency** — FTS index always in sync with metadata
3. **Sufficient for demo scale** — Handles thousands of documents efficiently
4. **GIN index** — Fast lookup for full-text queries

### Cross-Encoder
1. **Runs locally** — No API dependency, predictable latency
2. **Small model** — MiniLM-L-6 is fast even on CPU
3. **Proven quality** — MS MARCO trained models are well-benchmarked

## Negative Consequences

1. **PostgreSQL FTS is not full BM25** — Missing some tuning knobs of dedicated search engines
2. **Cross-encoder on CPU** — Slower than GPU; limits candidate set size
3. **Qdrant single-node** — Not horizontally scaled

## Alternatives Considered

### Vector DB
- **pgvector** — Embedded in PostgreSQL but lacks native payload filtering for ACLs. Rejected.
- **Weaviate** — Good features but heavier operational footprint. Rejected for simplicity.
- **Pinecone** — Managed service, good but adds cloud dependency. Rejected for local-first development.

### Keyword Index
- **Elasticsearch** — More powerful BM25 but adds significant infrastructure. Rejected for simplicity.
- **OpenSearch** — Same trade-offs as Elasticsearch. Rejected.

### Reranker
- **BGE reranker** — Good quality but larger model. Considered as alternative.
- **Cohere Rerank API** — Excellent quality but adds API dependency. Rejected for local-first approach.

## Future Review

- Upgrade to dedicated search engine if FTS becomes a bottleneck
- Evaluate GPU reranking if latency is too high
- Consider pgvector with manual ACL post-filtering if Qdrant operational costs become an issue
