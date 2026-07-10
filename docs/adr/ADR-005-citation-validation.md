# ADR-005: Citation Validation and Insufficient-Evidence Refusal

**Status:** Accepted  
**Date:** July 2025  
**Author:** Anushka Jain  

## Context

Enterprise knowledge systems must provide verifiable answers. LLMs frequently hallucinate citations — inventing page numbers, creating fake source references, or citing documents that weren't retrieved. Additionally, the system must handle cases where evidence is insufficient to answer a question without guessing.

## Decision

Implement a two-step post-generation validation:
1. **Citation validation** — Verify every [Source N] reference matches an actual retrieved chunk
2. **Evidence sufficiency assessment** — Classify evidence strength as strong/moderate/insufficient/conflicting

When evidence is insufficient or unauthorized, return an explicit refusal rather than a fabricated answer.

## Positive Consequences

1. **No fabricated citations** — Every citation points to real retrieved evidence
2. **Metadata accuracy** — Page numbers, row numbers, and sections come from retrieved chunk metadata, not LLM output
3. **Transparent confidence** — Users see evidence strength assessment
4. **Safe refusals** — System admits uncertainty rather than hallucinating
5. **Audit-friendly** — Citation validation status is logged

## Negative Consequences

1. **More refusals** — May refuse questions that could be partially answered
2. **Post-processing overhead** — Citation validation adds ~10-20ms per response
3. **Citation format dependency** — Requires LLM to follow [Source N] format consistently

## Alternatives Considered

1. **Trust LLM citations** — Accept whatever the LLM generates. Rejected because LLMs frequently hallucinate sources.
2. **Semantic citation matching** — Use similarity to match claims to sources. Rejected due to complexity and unreliability.
3. **Always answer** — Generate best-effort answer regardless of evidence. Rejected because enterprise users need reliable, verifiable information.

## Future Review

- Consider structured output (JSON mode) for more reliable citation extraction
- Evaluate claim-level grounding where each sentence is independently verified
- Consider confidence calibration using retrieval scores
