# Resume Bullets — SecureSource RAG

**Anushka Jain**

---

## Project Entry

**SecureSource RAG** — Permission-Aware Enterprise Knowledge Assistant  
*LLM Systems & Applied GenAI | July 2025*

- Designed and built a **permission-aware enterprise RAG system** that enforces document-level ACLs at retrieval time, ensuring unauthorized content never reaches the LLM context — eliminating the most common enterprise RAG security failure mode
- Implemented a **hybrid retrieval pipeline** combining dense vector search (Qdrant) with PostgreSQL full-text search, merged via Reciprocal Rank Fusion, achieving superior recall over dense-only baselines
- Built **source-aware chunking** across 5 enterprise formats (wiki, PDF, scanned OCR, Slack threads, spreadsheets), preserving document structure for citation-quality retrieval
- Created a **verifiable citation system** that validates every source reference against retrieved evidence, preventing LLM-generated hallucinated citations
- Engineered **prompt injection defenses** treating retrieved documents as untrusted data, with explicit security tests verifying resistance
- Developed a **100-question evaluation framework** measuring 12+ metrics including citation precision, retrieval recall, faithfulness, and security compliance
- Built production features including structured audit logging, safe refusals, duplicate detection, version tracking, and a responsive enterprise UI with 5 screens
- Tech stack: Python, FastAPI, Next.js, TypeScript, Qdrant, PostgreSQL, sentence-transformers, Tesseract OCR, Docker

---

## Skills Demonstrated

- Security Engineering (ACL design, threat modeling, prompt injection defense)
- ML/NLP Engineering (RAG, hybrid retrieval, re-ranking, evaluation)
- Backend Engineering (FastAPI, async Python, PostgreSQL, clean architecture)
- Frontend Engineering (Next.js, TypeScript, responsive design)
- System Design (modular architecture, service boundaries)
- Technical Documentation (ADRs, threat models, evaluation reports)
