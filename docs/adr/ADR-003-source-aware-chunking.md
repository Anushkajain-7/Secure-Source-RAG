# ADR-003: Source-Aware Structural Chunking Strategy

**Status:** Accepted  
**Date:** July 2025  
**Author:** Anushka Jain  

## Context

Document chunking directly impacts retrieval quality. A fixed-size character splitter treats all content identically, losing structural information critical for enterprise documents. Different source types have fundamentally different structures (headings vs tables vs threads) that require different chunking strategies.

## Decision

Implement **source-aware chunking** with distinct strategies for each document type:
- **Markdown/Wiki:** Split by heading hierarchy, preserving section context
- **PDF:** Split by section and paragraph, respecting page boundaries
- **Slack:** Keep parent message + replies together as a unit
- **Spreadsheet:** Group related rows with column headers

## Positive Consequences

1. **Preserves document structure** — Headings stay with their content, table rows stay together
2. **Better retrieval quality** — Chunks contain coherent, self-contained information
3. **Richer citations** — Source-specific metadata (page, section, thread, row) enables precise citations
4. **Reduces context pollution** — Avoids mixing unrelated content from different sections

## Negative Consequences

1. **Variable chunk sizes** — Harder to predict token usage; some chunks may be very small or very large
2. **Implementation complexity** — Four separate chunking implementations to maintain
3. **Parser dependency** — Chunking quality depends on parser quality

## Alternatives Considered

1. **Fixed character split (RecursiveCharacterTextSplitter)** — Simple but loses structure. Rejected because it splits headings from content, breaks table rows, and mixes thread contexts.
2. **Sentence-level splitting** — Better than character splitting but still loses hierarchical structure. Rejected for similar reasons.
3. **Semantic chunking** — Using embeddings to find natural break points. Rejected due to computational cost and inconsistent results on structured content.

## Future Review

- Consider adaptive chunk sizing based on content density
- Evaluate late chunking approaches for improved context retention
