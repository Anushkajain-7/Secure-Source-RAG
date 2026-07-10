# ADR-002: ACL Filtering Before LLM Context Construction

**Status:** Accepted  
**Date:** July 2025  
**Author:** Anushka Jain  

## Context

Enterprise RAG systems must enforce access control. Two architectural approaches exist: (1) filter unauthorized content **before** it reaches the LLM context, or (2) retrieve all content, generate an answer, then filter unauthorized information from the response **after** generation.

## Decision

Enforce ACL filtering **before** any unauthorized content enters the LLM context. Implement three-layer filtering:
1. Qdrant payload-based filtering during dense retrieval
2. PostgreSQL WHERE clauses during keyword retrieval
3. Final ACL verification gate before context construction

## Positive Consequences

1. **Information never leaked** — Unauthorized content is never seen by the LLM, so it cannot be inadvertently included in answers
2. **No metadata leakage** — The LLM never sees restricted document titles, snippets, or source references
3. **Simpler generation** — The LLM only works with authorized content, reducing prompt complexity
4. **Audit clarity** — Clear separation between "retrieved" and "authorized" at each step
5. **Defense in depth** — Three filtering layers provide redundancy

## Negative Consequences

1. **Potential answer quality reduction** — If relevant context is filtered out, the answer may be less complete
2. **False negatives** — Overly restrictive filters might exclude legitimately accessible content
3. **Requires denormalized ACLs** — Chunk-level ACL metadata must be maintained for efficient filtering

## Alternatives Considered

1. **Post-generation filtering** — Retrieve all, generate answer, then redact. Rejected because the LLM context already contains unauthorized data, creating information leakage risk.
2. **Prompt-based filtering** — Include ACL instructions in the prompt asking the LLM to ignore restricted content. Rejected because LLMs are unreliable at following access control instructions.
3. **Separate authorized/unauthorized retrieval** — Run retrieval twice. Rejected due to performance and complexity concerns.

## Rejected Alternative Deep Dive

Post-generation filtering is the most common anti-pattern in enterprise RAG. Even if restricted content is redacted from the final answer, the LLM may:
- Synthesize restricted information into seemingly innocuous statements
- Reveal restricted document existence through comparative analysis
- Leak metadata (filenames, sections) in citations
- Be manipulated through prompt injection to reveal filtered content

## Future Review

- If false negatives become a significant problem, consider a "borderline access" review queue
- Evaluate fine-grained permission inheritance for nested document structures
