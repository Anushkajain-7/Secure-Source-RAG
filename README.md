<p align="center">
  <h1 align="center">🔒 SecureSource RAG</h1>
  <p align="center">
    <strong>A permission-aware enterprise knowledge assistant that securely answers questions across PDFs, scanned documents, wiki pages, Slack-style conversations, and spreadsheets — with verifiable inline citations.</strong>
  </p>
  <p align="center">
    <a href="#demo">Demo</a> •
    <a href="#features">Features</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#security">Security</a> •
    <a href="#evaluation">Evaluation</a>
  </p>
</p>

---

## 🎯 Demo

| Resource | Link |
|----------|------|
| **Live Demo** | `[PLACEHOLDER — deployment URL]` |
| **Loom Walkthrough** | `[PLACEHOLDER — Loom URL]` |
| **Repository** | `[PLACEHOLDER — GitHub URL]` |

---

## 📋 Problem Statement

Enterprise organizations store critical knowledge across dozens of disconnected systems — Confluence wikis, PDF policies, Slack conversations, spreadsheets, and scanned documents. Employees waste hours searching for information, and when they find it, they can't verify whether it's current or authorized for their role.

Existing "chat with your docs" solutions fail enterprises because they:
- **Ignore access control** — returning confidential data to unauthorized users
- **Don't handle messy formats** — breaking on scanned PDFs, spreadsheets, and threaded conversations
- **Lack citations** — making claims without verifiable evidence
- **Miss version conflicts** — treating outdated policies as current

**SecureSource RAG** solves these problems with **security-first retrieval**: permissions are enforced **before** any document reaches the LLM context, not after.

## 💼 Business Value

- **Reduce knowledge search time** from hours to seconds
- **Enforce access control** across all enterprise knowledge
- **Provide verifiable citations** for every claim
- **Handle real enterprise formats** including scanned documents and spreadsheets
- **Detect and deprioritize outdated** or conflicting documents
- **Maintain audit trails** for compliance and security

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **Role-Based Access Control** | Document-level and chunk-level ACLs enforced at retrieval time |
| 📄 **Multi-Format Support** | Markdown, PDF, scanned PDF (OCR), Slack JSON, Excel, CSV |
| 🔍 **Hybrid Retrieval** | Dense vector + keyword search with reciprocal rank fusion |
| 📊 **Source-Aware Chunking** | Different strategies for wikis, PDFs, threads, and tables |
| 📎 **Inline Citations** | Every claim linked to source with page, section, or row reference |
| 🛡️ **Prompt Injection Defense** | Retrieved content treated as untrusted data |
| 🔄 **Version Detection** | Identifies and deprioritizes outdated documents |
| ⚖️ **Conflict Resolution** | Explicitly states when sources conflict |
| 🚫 **Safe Refusals** | Refuses when evidence is insufficient or unauthorized |
| 📈 **Evaluation Framework** | 100-question dataset with comprehensive metrics |
| 📋 **Audit Logging** | Every query logged with user, chunks, and decisions |
| 🏢 **Enterprise UI** | Login, Q&A, source management, evaluation, and audit dashboards |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js + Tailwind)             │
│  Login │ Ask SecureSource │ Sources │ Evaluation │ Audit     │
└────────────────────────────┬────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼────────────────────────────────┐
│                    Backend (FastAPI + Python)                │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │   Auth   │  │ Ingestion│  │Retrieval │  │ Generation │  │
│  │& Perms   │  │ Pipeline │  │ Pipeline │  │ + Citations│  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └─────┬──────┘  │
│       │              │             │               │         │
│  ┌────▼─────────────▼─────────────▼───────────────▼──────┐  │
│  │              Security Engine (ACL Filters)             │  │
│  └────────────────────┬──────────────────────────────────┘  │
│                       │                                      │
│  ┌────────────────────▼──────────────────────────────────┐  │
│  │                 Audit Logger                           │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────┬─────────────────────────────┬────────────────┘
               │                             │
    ┌──────────▼──────────┐       ┌──────────▼──────────┐
    │   PostgreSQL 16     │       │    Qdrant Vector     │
    │ Metadata + FTS +    │       │    Store (Dense      │
    │ Audit + Evaluation  │       │    Retrieval + ACL   │
    └─────────────────────┘       │    Payload Filter)   │
                                  └─────────────────────┘
```

### Retrieval Pipeline (Security-First)

```
User Question
    → Authenticate User
    → Build ACL Filter (departments, access_levels, roles)
    → Query Rewriting / Expansion
    → Dense Retrieval (Qdrant) with ACL Payload Filter
    → Keyword Retrieval (PostgreSQL FTS) with ACL WHERE Clause
    → Reciprocal Rank Fusion (merge results)
    → Deduplicate
    → Cross-Encoder Re-ranking
    → Final ACL Verification Gate
    → Context Construction (authorized chunks only)
    → LLM Generation (security-hardened system prompt)
    → Citation Validation
    → Return Answer + Citations
    → Log Audit Record
```

**Critical Security Rule:** Unauthorized chunks never enter the LLM context. Filtering happens at retrieval time, not after generation.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui | Modern reactive UI |
| Backend | Python 3.11, FastAPI, Pydantic v2 | Type-safe async API |
| Vector DB | Qdrant | Dense retrieval with metadata filtering |
| Metadata DB | PostgreSQL 16 | Metadata, FTS, audit, evaluation |
| PDF Parsing | PyMuPDF | Text extraction and table detection |
| OCR | Tesseract (pytesseract) | Scanned PDF processing |
| Spreadsheets | Pandas, OpenPyXL | Excel and CSV parsing |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Local embedding generation |
| Re-ranker | cross-encoder/ms-marco-MiniLM-L-6-v2 | Cross-encoder re-ranking |
| LLM | HuggingFace Inference API (primary), OpenAI (fallback) | Answer generation |
| Logging | structlog | Structured JSON logging |
| Testing | pytest, pytest-asyncio | Backend testing |
| DevOps | Docker, Docker Compose, GitHub Actions | Containerized deployment |

---

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 20+
- A HuggingFace API key (free at [huggingface.co](https://huggingface.co))

### Installation

```bash
# 1. Clone the repository
git clone <PLACEHOLDER_GITHUB_URL>
cd secure-source-rag

# 2. Create environment file
cp .env.example .env
# Edit .env and add your HUGGINGFACE_API_KEY

# 3. Start infrastructure (PostgreSQL + Qdrant)
docker compose up -d postgres qdrant

# 4. Install backend dependencies
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# 5. Start the backend
cd ..
PYTHONPATH=. uvicorn backend.main:app --reload --port 8000

# 6. (In a new terminal) Install and start the frontend
cd frontend
npm install
npm run dev

# 7. Seed the sample data
cd ..
PYTHONPATH=. python scripts/seed_data.py
```

### Docker Compose (Full Stack)

```bash
cp .env.example .env
# Edit .env with your API key
docker compose up --build
```

The application will be available at:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `HUGGINGFACE_API_KEY` | Yes | HuggingFace Inference API key |
| `LLM_PROVIDER` | No | `huggingface` (default) or `openai` |
| `OPENAI_API_KEY` | If using OpenAI | OpenAI API key |
| `POSTGRES_PASSWORD` | Yes | PostgreSQL password |
| `APP_SECRET_KEY` | Yes | Application secret key |

See [.env.example](.env.example) for all configuration options.

---

## 👥 Demo Users

| User | Role | Department | Access Scope |
|------|------|-----------|--------------|
| **Aarav Sharma** | General Employee | General | Public policies, announcements, handbook |
| **Anushka Jain** | Software Engineer | Engineering | General + engineering docs, incidents, Slack |
| **Meera Kapoor** | HR Manager | HR | General + HR policies, salary bands, hiring |
| **Rohan Mehta** | Finance Analyst | Finance | General + finance reports, budgets |
| **Admin User** | Administrator | Leadership | All documents + admin panels |

---

## 💬 Sample Questions

### Any User
- "What is the annual leave policy?"
- "What are the company working hours?"
- "What is the dress code policy?"

### Engineering (Anushka)
- "Which engineering team owns the payment service?"
- "What caused the latest production outage?"
- "What was discussed in the engineering incident Slack thread?"

### HR (Meera)
- "What are the salary-band rules for senior engineers?"
- "Compare domestic and international travel policies."

### Finance (Rohan)
- "What was the approved Q2 marketing budget?"

### Admin
- "What are the leadership strategic priorities?"

---

## 📁 Data Sources

| Type | Count | Examples |
|------|-------|---------|
| Markdown/Wiki | 8+ | Leave policy, employee handbook, engineering ownership |
| PDF | 5+ | Incident reports, architecture docs |
| Scanned PDF | 2+ | Legacy reports |
| Slack JSON | 3+ | Engineering incidents, general discussion |
| CSV/Excel | 3+ | Budget reports, headcount data |

All data is **synthetic** — created for the fictional company BigCorp. No real company data is used.

---

## 🔐 Security Model

### Access Control
- **Document-level ACLs**: Each document has department, access_level, allowed_roles, allowed_users
- **Chunk-level inheritance**: Every chunk inherits its parent document's permissions
- **Retrieval-time filtering**: ACLs enforced in both Qdrant payload filters and PostgreSQL WHERE clauses
- **Citation authorization**: Post-generation validation ensures no unauthorized sources appear

### Prompt Injection Defense
- Retrieved content wrapped in data delimiters
- System prompt contains explicit override protection
- Test document with injection attempt included in dataset

### Safe Refusals
- Returns "I could not find sufficient authorized evidence" instead of hallucinating
- Never reveals whether a restricted document exists

### Audit Trail
- Every query logged: user, question, chunks, decision, latency, errors

---

## 📊 Evaluation

### Dataset
100 structured evaluation questions across 8 categories:
- Simple factual (20), Spreadsheet/table (15), Multi-source (15)
- OCR (10), Slack (10), Duplicate/conflict (10)
- Summarization (10), Permission/security (10)

### Metrics
| Metric | Status |
|--------|--------|
| Answer Accuracy | `[PENDING]` |
| Citation Precision | `[PENDING]` |
| Citation Recall | `[PENDING]` |
| Retrieval Recall@5 | `[PENDING]` |
| Faithfulness | `[PENDING]` |
| Correct Refusal Rate | `[PENDING]` |
| Unauthorized Retrieval Rate | `[PENDING]` |
| Prompt Injection Resistance | `[PENDING]` |
| Avg Latency (ms) | `[PENDING]` |

Metrics will be populated after evaluation runs are executed.

---

## ⚠️ Known Limitations

1. Demo authentication — no real OAuth/SSO
2. Embedding and reranker models run on CPU (slower without GPU)
3. OCR quality depends on scan quality
4. HuggingFace Inference API has rate limits
5. No real-time document sync — batch ingestion only
6. Single-node deployment — not horizontally scaled

---

## 🗺️ Roadmap

- [ ] Real authentication (OAuth2 / SAML)
- [ ] Streaming responses
- [ ] Multi-turn conversation
- [ ] Document change detection and auto-reindex
- [ ] GPU-accelerated embedding and reranking
- [ ] Horizontal scaling with Kubernetes
- [ ] Fine-tuned embedding model for enterprise vocabulary
- [ ] Integration with real Confluence/Slack/Google Drive APIs

---

## 📚 ADR Links

- [ADR-001: Hybrid Retrieval vs Dense-Only](docs/adr/ADR-001-hybrid-retrieval.md)
- [ADR-002: ACL Filtering Before LLM Context](docs/adr/ADR-002-acl-filtering.md)
- [ADR-003: Source-Aware Chunking](docs/adr/ADR-003-source-aware-chunking.md)
- [ADR-004: Vector DB and Reranker Selection](docs/adr/ADR-004-vector-db-selection.md)
- [ADR-005: Citation Validation and Refusal](docs/adr/ADR-005-citation-validation.md)
- [ADR-006: Duplicate Detection](docs/adr/ADR-006-duplicate-detection.md)

---

## 🧪 Testing

```bash
# Run all tests
cd backend
PYTHONPATH=.. pytest tests/ -v

# Run with coverage
PYTHONPATH=.. pytest tests/ -v --cov=backend --cov-report=html
```

---

## 📜 License

MIT License. See [LICENSE](LICENSE).

---

## 🙏 Acknowledgements

- [LlamaIndex](https://github.com/run-llama/llama_index) — RAG framework
- [Qdrant](https://qdrant.tech/) — Vector database
- [PyMuPDF](https://pymupdf.readthedocs.io/) — PDF processing
- [sentence-transformers](https://www.sbert.net/) — Embeddings and reranking
- [FastAPI](https://fastapi.tiangolo.com/) — Backend framework
- [shadcn/ui](https://ui.shadcn.com/) — UI components

---

## 🎯 What This Project Demonstrates to Recruiters

This project demonstrates competency in:

1. **Security Engineering** — ACL enforcement, prompt injection defense, safe refusals, audit logging
2. **ML/NLP Engineering** — Hybrid retrieval, reranking, embedding pipelines, evaluation frameworks
3. **Backend Engineering** — FastAPI, PostgreSQL, async Python, clean architecture
4. **Frontend Engineering** — Next.js, TypeScript, responsive enterprise UI
5. **DevOps** — Docker, CI/CD, environment management
6. **System Design** — Multi-component architecture, service boundaries, data modeling
7. **Technical Documentation** — ADRs, threat models, evaluation reports
8. **Product Thinking** — User-centric design, realistic scenarios, edge case handling

**Author:** Anushka Jain  
**Segment:** LLM Systems & Applied GenAI  
**Problem Code:** E3
