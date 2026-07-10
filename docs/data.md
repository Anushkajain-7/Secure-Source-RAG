# SecureSource RAG — Data Documentation

**Author:** Anushka Jain  
**Date:** July 2025  

---

## Source Types

| Type | Format | Parser | Count (Target) |
|------|--------|--------|----------------|
| Wiki/Markdown | `.md` with YAML frontmatter | `markdown_parser.py` | 20-30 |
| Text PDF | `.pdf` | `pdf_parser.py` (PyMuPDF) | 15-25 |
| Scanned PDF | `.pdf` (image-based) | `ocr_parser.py` (Tesseract) | 5-8 |
| Slack JSON | `.json` | `slack_parser.py` | 15-25 threads |
| Excel | `.xlsx` | `spreadsheet_parser.py` (pandas) | 8-12 |
| CSV | `.csv` | `spreadsheet_parser.py` (pandas) | included above |

## Synthetic Data Explanation

All data is **entirely synthetic**, created for the fictional company **BigCorp**. No real company data, employee information, or confidential material is used.

The data is designed to test specific RAG capabilities:
- Multi-format parsing
- Access control enforcement
- Version detection
- Duplicate handling
- Citation generation
- Prompt injection resistance

## Dataset Structure

```
sample_data/
├── markdown/                    # Wiki-style documents
│   ├── annual_leave_policy_v2.md       # Current leave policy
│   ├── annual_leave_policy_v1_outdated.md  # Outdated version
│   ├── employee_handbook.md            # General handbook
│   ├── travel_reimbursement_policy.md  # Travel policy
│   ├── engineering_team_ownership.md   # Engineering doc
│   ├── salary_bands_confidential.md    # RESTRICTED - HR only
│   ├── leadership_strategic_priorities_confidential.md  # CONFIDENTIAL
│   └── malicious_prompt_injection.md   # Prompt injection test
├── pdf/                         # Text-based PDFs
├── scanned_pdf/                 # OCR-required PDFs
├── slack/                       # Threaded conversations
│   └── engineering_incidents.json
├── spreadsheets/                # Budget and data files
│   └── q1_q2_budget_report.csv
└── evaluation/                  # 100-question eval dataset
```

## Schema

Every document is normalized to the canonical schema:

| Field | Type | Description |
|-------|------|-------------|
| document_id | UUID | Unique document identifier |
| source_type | enum | markdown, pdf, scanned_pdf, slack, spreadsheet |
| source_name | text | Original filename |
| source_title | text | Document title |
| department | enum | general, engineering, hr, finance, leadership |
| allowed_roles | text[] | Roles with explicit access |
| allowed_users | text[] | Users with explicit access |
| access_level | enum | public, department, restricted, confidential |
| version | int | Document version number |
| is_current_version | bool | Whether this is the current version |
| content_hash | text | SHA-256 of raw content |
| source_trust_level | enum | official, approved, informal, unverified |

## Access Control Fields

Documents are tagged with ACL metadata at ingestion time:

- **public** — Accessible to all authenticated users
- **department** — Accessible to users in the same department + general
- **restricted** — Accessible only to specified roles (e.g., HR Manager)
- **confidential** — Accessible only to administrators

## Licensing Status

All synthetic data is original content created for this project. No copyrighted material is included. Licensed under MIT.

## Privacy Precautions

- No real employee names, salaries, or personal data
- All company names are fictional
- Email addresses use fictional domains (@bigcorp.com)
- Financial figures are fabricated
- Policy content is original, not copied from real companies

## Data Generation Process

1. Manual creation of realistic enterprise documents
2. YAML frontmatter for metadata
3. Structured JSON for Slack conversations
4. CSV/Excel for structured data
5. Each document tagged with appropriate department and access level

## Known Limitations

- Synthetic data may not capture all real-world document complexities
- Scanned PDFs are generated from text (not actual physical scans)
- Slack data uses simplified message format (not full Slack API export)
- Spreadsheet data is relatively simple (no complex formulas or pivot tables)
