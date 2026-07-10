# SecureSource RAG — Showcase Slide Content

**Format:** 16:9 Professional Slide  
**Visual Style:** Enterprise AI — dark gradient background, clean typography  

---

## Slide Layout

### Header
**🔒 SecureSource RAG**  
*Permission-Aware Enterprise Knowledge Assistant*

### Problem (Left Column)
Enterprise employees can't safely search internal knowledge across PDFs, wikis, Slack, and spreadsheets — existing RAG solutions leak confidential data to unauthorized users.

### Architecture Flow (Center)
```
Question → Auth → ACL Filter → Hybrid Retrieval → Re-rank → Generate → Cite → Answer
                     ↑                                              ↑
              Unauthorized content                         Citation validation
              NEVER reaches LLM                            ensures accuracy
```

### Four Source Types (Icons Row)
📄 Wiki/Markdown | 📑 PDF + OCR | 💬 Slack Threads | 📊 Spreadsheets

### Security Differentiator (Highlighted Box)
**"Permissions enforced BEFORE retrieval, not after generation"**
- Document-level ACLs with chunk inheritance
- Three-layer filtering: Qdrant → PostgreSQL → Verification Gate
- Prompt injection defense + safe refusals

### Evaluation Metrics (Right Column)
| Metric | Value |
|--------|-------|
| Questions | 100 |
| Source Types | 5 |
| Security Tests | ✅ |
| Citation Validation | ✅ |
| Safe Refusals | ✅ |

### Technology Stack (Bottom Strip)
`Python` `FastAPI` `Next.js` `Qdrant` `PostgreSQL` `sentence-transformers` `Tesseract` `Docker`

### Footer
**Anushka Jain** | LLM Systems & Applied GenAI | E3  
🔗 GitHub: `[PLACEHOLDER]` | 🌐 Demo: `[PLACEHOLDER]` | 📱 QR: `[PLACEHOLDER]`
