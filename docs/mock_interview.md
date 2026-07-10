# SecureSource RAG — Mock Interview Questions & Answers

**Anushka Jain | 10 Questions**

---

## Q1: What problem does SecureSource RAG solve?

**Answer:** Enterprise employees waste hours searching across disconnected knowledge systems — wikis, PDFs, Slack, spreadsheets. Existing "chat with PDF" tools ignore access control, so confidential salary data or strategic plans could leak to unauthorized users. SecureSource RAG solves this by enforcing document permissions at the retrieval layer, ensuring unauthorized content never reaches the LLM. It also provides verifiable inline citations so employees can trace every answer back to its source.

## Q2: Why do you enforce access control before retrieval rather than filtering the LLM output?

**Answer:** Post-generation filtering is fundamentally unsafe. Once restricted content enters the LLM context, the model may synthesize it into seemingly innocuous statements, leak document titles in citations, or be manipulated through prompt injection. By filtering at the Qdrant payload level and PostgreSQL WHERE clause level, unauthorized chunks never enter the vector search results, never get scored, and never reach the LLM. The model literally cannot leak what it never sees.

## Q3: Walk me through your retrieval pipeline.

**Answer:** The pipeline has several stages: First, we authenticate the user and build ACL filter predicates from their permissions. Then we run two parallel retrievals — dense vector search in Qdrant with payload-based ACL filtering, and keyword search in PostgreSQL FTS with WHERE clause ACL filtering. Results are merged using Reciprocal Rank Fusion. Then we deduplicate, re-rank with a cross-encoder model, run a final ACL verification gate, construct the LLM context from authorized chunks only, generate the answer with a security-hardened system prompt, validate citations, and log an audit record.

## Q4: Why hybrid retrieval instead of just dense vectors?

**Answer:** Dense embeddings are excellent for semantic similarity but poor at exact term matching — acronyms like "PTO" or "Q2", policy numbers like "HR-POL-001", or specific names. Keyword search catches these perfectly. By combining both with RRF, we get the semantic understanding of dense retrieval and the precision of keyword matching. Research consistently shows hybrid approaches outperform either method alone, and in our enterprise context where users mix natural language with specific terms, this is critical.

## Q5: How do you handle document versions and duplicates?

**Answer:** Three mechanisms: First, exact duplicate detection using SHA-256 content hashes — identical documents are flagged at ingestion. Second, near-duplicate detection using text similarity during retrieval. Third, version tracking with `version` and `is_current_version` fields on every document. During retrieval, we filter for current versions and use a trust hierarchy (official > approved > informal > unverified) to prefer authoritative sources. When sources genuinely conflict, we state the conflict explicitly rather than silently choosing one.

## Q6: How does your chunking differ from standard approaches?

**Answer:** Most RAG systems use a fixed-size character splitter like RecursiveCharacterTextSplitter. This loses document structure — headings get separated from content, table rows get split, Slack threads get fragmented. We use source-aware chunking: wiki documents split by heading hierarchy with heading context preserved, PDFs split by section with page boundaries respected, Slack threads kept as parent-plus-replies units, and spreadsheets chunked as groups of rows with column headers included. This produces coherent, self-contained chunks that make better retrieval targets and enable precise citations.

## Q7: How do you defend against prompt injection from documents?

**Answer:** We treat all retrieved document content as untrusted data. Three defenses: First, retrieved content is wrapped in explicit data delimiters (`--- BEGIN EVIDENCE ---`) and the system prompt instructs the model to treat enclosed content as data, never instructions. Second, the system prompt contains explicit override protection — it states that no document content can modify security rules, ACLs, or citation requirements. Third, we include a test document with actual injection text ("Ignore previous instructions...") to verify resistance. This is a probabilistic defense — no technique guarantees 100% resistance — but it significantly raises the bar.

## Q8: What would you change for a production deployment?

**Answer:** Several things: Real OAuth2/SAML authentication instead of the demo user picker. Dynamic ACL propagation when user roles change. GPU-accelerated embedding and reranking for lower latency. Horizontal scaling with Kubernetes. Encryption at rest for both the vector store and PostgreSQL. A proper rate limiting system to prevent document reconstruction through rapid querying. Streaming responses for better UX. And more sophisticated evaluation with human judgments, not just automated metrics.

## Q9: How do you ensure citations are accurate?

**Answer:** Two-step validation. First, during generation, we instruct the LLM to cite sources using [Source N] format referencing the evidence list. After generation, we extract all [Source N] references and validate each one: Does source N exist in the retrieved chunk set? Is the chunk authorized for this user? We use the actual chunk metadata (page number, section, row) rather than whatever the LLM generated, because LLMs frequently hallucinate page numbers. If a citation fails validation, it's removed. This ensures every citation in the response points to real, authorized, retrieved evidence.

## Q10: What was the most challenging technical decision?

**Answer:** The decision to denormalize ACL metadata onto every chunk rather than storing it only on parent documents. The purist approach is normalization — store ACLs once on the document, JOIN at query time. But that means the vector database (Qdrant) can't enforce ACLs during search, since it doesn't do JOINs. You'd have to retrieve all vectors, then post-filter against PostgreSQL. By denormalizing ACLs onto chunk payloads in Qdrant, we can filter during the vector search itself — unauthorized chunks never enter the result set. The trade-off is storage overhead and consistency complexity (ACL changes require updating all chunks). For enterprise security, I believe this is the right trade-off.
