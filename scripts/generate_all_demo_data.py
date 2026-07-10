import os
import json
import uuid
import csv
from pathlib import Path
from PIL import Image
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Base folders
data_root = Path("sample_data")
pdf_dir = data_root / "pdf"
scanned_pdf_dir = data_root / "scanned_pdf"
slack_dir = data_root / "slack"
spreadsheet_dir = data_root / "spreadsheet"

for d in [pdf_dir, scanned_pdf_dir, slack_dir, spreadsheet_dir]:
    d.mkdir(parents=True, exist_ok=True)

print("🚀 Starting programmatic generation of Batches 2, 3, and 4...")

# Helper: Create text PDF
def create_text_pdf(filepath, title, lines):
    c = canvas.Canvas(str(filepath), pagesize=letter)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, 750, title)
    c.setLineWidth(1)
    c.line(100, 740, 500, 740)
    
    c.setFont("Helvetica", 11)
    y = 700
    for line in lines:
        if y < 100:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = 750
        c.drawString(100, y, line)
        y -= 20

    # Draw standard headers/footers for edge case
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(100, 40, "CONFIDENTIAL - BIGCORP INTERNAL USE ONLY")
    c.drawString(500, 40, "Page 1")
    c.save()

# Helper: Convert normal PDF to fully scanned PDF
def convert_to_scanned(input_pdf_path, output_pdf_path):
    doc = fitz.open(str(input_pdf_path))
    images = []
    for page in doc:
        pix = page.get_pixmap(dpi=150)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    if images:
        images[0].save(str(output_pdf_path), save_all=True, append_images=images[1:])
    doc.close()

# Helper: Create sidecar metadata
def write_sidecar(filepath, meta_dict):
    if "department" in meta_dict and meta_dict["department"]:
        meta_dict["department"] = meta_dict["department"].lower()
    if "access_level" in meta_dict and meta_dict["access_level"]:
        meta_dict["access_level"] = meta_dict["access_level"].lower()
    meta_path = filepath.with_suffix(filepath.suffix + ".json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_dict, f, indent=2)

# ==========================================
# BATCH 2: PDFs and Scanned PDFs
# ==========================================
print("📁 Generating Batch 2: PDFs...")

# 15 Normal PDFs
normal_pdfs = [
    {
        "filename": "engineering_architecture_standards.pdf",
        "title": "Engineering Architecture Standards",
        "department": "ENGINEERING",
        "access_level": "RESTRICTED",
        "allowed_roles": ["Software Engineer", "Administrator"],
        "lines": [
            "This document establishes the architecture standards for all backend software groups.",
            "All new services must be deployed in containerized Kubernetes clusters.",
            "Database transactions must prioritize Spanner for multi-region active-active workloads.",
            "Redis must be used for distributed caching with eviction policies set to volatile-lru.",
            "For FTS and hybrid search, Elasticsearch or postgres FTS is the standard.",
            "APIs must strictly implement OAuth2 tokens and TLS 1.3 encryption."
        ],
        "description": "Standard architecture and framework guidelines for backend engineering."
    },
    {
        "filename": "hr_conduct_policy.pdf",
        "title": "Employee Code of Conduct",
        "department": "HR",
        "access_level": "PUBLIC",
        "allowed_roles": [],
        "lines": [
            "BigCorp requires all employees to maintain a professional, respectful work environment.",
            "Harassment, discrimination, and unethical business practices are strictly prohibited.",
            "Conflicts of interest must be disclosed to HR within 5 business days.",
            "Gifts from vendors or partners exceeding $50 in value must be reported and approved.",
            "Remote work hours must align with standard team schedules unless agreed in writing."
        ],
        "description": "Company guidelines for professional behavior and business ethics."
    },
    {
        "filename": "finance_travel_expense_guidelines.pdf",
        "title": "Finance Travel Expense Guidelines",
        "department": "FINANCE",
        "access_level": "PUBLIC",
        "allowed_roles": [],
        "lines": [
            "All business travel expenses must be submitted through Expensify within 30 days of trip completion.",
            "Meal expenses are covered up to a daily per diem rate of $60.",
            "Domestic hotel accommodations are reimbursed up to $150 per night.",
            "Original receipts are required for any individual expense item exceeding $25.",
            "First-class air travel is prohibited unless pre-authorized by the Chief Financial Officer."
        ],
        "description": "Reimbursement rules, limits, and submission workflows for business travel."
    },
    {
        "filename": "leadership_board_minutes_q1_2026.pdf",
        "title": "Board of Directors Minutes - Q1 2026",
        "department": "LEADERSHIP",
        "access_level": "CONFIDENTIAL",
        "allowed_roles": ["Administrator"],
        "lines": [
            "Board meeting held on January 22, 2026. All board members present.",
            "CEO presented the Q1 strategic goals, highlighting M&A targets in the AI space.",
            "The acquisition of TechStartup Corp for $45M was discussed and approved in principle.",
            "Finance committee recommended keeping current interest rate hedges in place.",
            "Next board meeting scheduled for April 15, 2026 to review Q1 performance numbers."
        ],
        "description": "Minutes of the Board of Directors Q1 meeting. Contains sensitive M&A and strategic decisions."
    },
    {
        "filename": "general_workplace_safety.pdf",
        "title": "Workplace Safety and Emergency Procedures",
        "department": "GENERAL",
        "access_level": "PUBLIC",
        "allowed_roles": [],
        "lines": [
            "Welcome to BigCorp office facilities. Your safety is our highest priority.",
            "In case of fire, use the nearest stairwell. Do not use the elevators under any circumstances.",
            "First-aid kits are located on every floor near the elevator lobby pantry.",
            "Emergency contacts list is posted in the main kitchen on the third floor.",
            "Report any workplace hazards or suspicious visitors to building security immediately."
        ],
        "description": "Safety protocols, evacuation routes, and emergency guidelines for office locations."
    }
]

# We will generate these 5 normal PDFs, and then add 10 more simple ones to reach 15.
for idx in range(6, 16):
    normal_pdfs.append({
        "filename": f"general_policy_doc_{idx}.pdf",
        "title": f"General Policy Document No. {idx}",
        "department": "GENERAL",
        "access_level": "PUBLIC",
        "allowed_roles": [],
        "lines": [
            f"This is policy document number {idx} detailing general administrative operations.",
            "Standard operating procedures must be followed for office visits.",
            "Ensure that badges are visible at all times when inside the facility.",
            "Recycling bins are color-coded: blue for paper, green for plastics, black for landfill."
        ],
        "description": f"Standard operational document {idx} for general business guidelines."
    })

for doc in normal_pdfs:
    path = pdf_dir / doc["filename"]
    create_text_pdf(path, doc["title"], doc["lines"])
    write_sidecar(path, {
        "title": doc["title"],
        "department": doc["department"],
        "access_level": doc["access_level"],
        "allowed_roles": doc["allowed_roles"],
        "allowed_users": [],
        "version": 1,
        "is_current_version": True,
        "source_trust_level": "official",
        "description": doc["description"]
    })

# 5 Scanned PDFs
scanned_pdfs = [
    {
        "filename": "scanned_leadership_executive_contract.pdf",
        "title": "Executive Employment Contract - CEO",
        "department": "LEADERSHIP",
        "access_level": "CONFIDENTIAL",
        "allowed_roles": ["Administrator"],
        "lines": [
            "EXECUTIVE EMPLOYMENT AGREEMENT",
            "This contract is made between BigCorp Inc. and Johnathan Miller (Chief Executive Officer).",
            "Effective date: February 1, 2026.",
            "Base compensation: $450,000 base salary per annum, paid monthly.",
            "Performance bonus: Up to 50% of base salary contingent on Board metrics.",
            "Equity grants: 100,000 options vesting over 4 years with a 1-year cliff.",
            "Termination clause: 12 months severance if terminated without cause."
        ],
        "description": "Scanned contract of executive employment detailing CEO salary, equity, and severance."
    },
    {
        "filename": "scanned_hr_signed_offer_letter.pdf",
        "title": "Signed Offer Letter - Senior Director",
        "department": "HR",
        "access_level": "RESTRICTED",
        "allowed_roles": ["HR Manager", "Administrator"],
        "lines": [
            "CONFIDENTIAL EMPLOYMENT OFFER",
            "Dear Sarah Jenkins,",
            "We are pleased to offer you the position of Senior Director of Talent Acquisition.",
            "Salary: $185,000 base per year.",
            "Sign-on bonus: $20,000 paid on your first pay cycle.",
            "Start date: August 1, 2026.",
            "Signed: Sarah Jenkins (Signed via DocuSign on June 12, 2026)"
        ],
        "description": "Scanned copy of signed employment offer letter for Sarah Jenkins."
    },
    {
        "filename": "scanned_finance_vendor_invoice.pdf",
        "title": "Vendor Invoice - CloudService Corp",
        "department": "FINANCE",
        "access_level": "RESTRICTED",
        "allowed_roles": ["Finance Analyst", "Administrator"],
        "lines": [
            "CLOUDSERVICE CORP - INVOICE # INV-2026-9908",
            "Bill to: BigCorp Finance Dept (Accounts Payable)",
            "Invoice Date: July 1, 2026.",
            "Services rendered: Enterprise Cloud Storage and compute - June 2026.",
            "Amount due: $84,320.50.",
            "Payment terms: Net 30.",
            "Bank details: Chase Manhattan, Acct: 99881122, Routing: 021000021."
        ],
        "description": "Scanned vendor invoice for monthly cloud services."
    },
    {
        "filename": "scanned_engineering_patent_application.pdf",
        "title": "US Patent Application Draft - AI Data Retrieval",
        "department": "ENGINEERING",
        "access_level": "DEPARTMENT",
        "allowed_roles": ["Software Engineer", "Administrator"],
        "lines": [
            "PATENT SPECIFICATION DRAFT - CONFIDENTIAL",
            "Title: A Method for Permission-Aware Vector Search in Retrieval-Augmented Generation",
            "Inventors: Anushka Jain, Rohan Mehta.",
            "Abstract: This invention describes a vector search algorithm that injects user group ACL filters",
            "directly into the database indexing engine to prune search results before similarity calculation.",
            "Assignee: BigCorp Tech Holdings."
        ],
        "description": "Scanned patent application draft for permission-aware RAG vector search."
    },
    {
        "filename": "scanned_general_facilities_agreement.pdf",
        "title": "Facilities Maintenance Agreement",
        "department": "GENERAL",
        "access_level": "PUBLIC",
        "allowed_roles": [],
        "lines": [
            "FACILITIES MAINTENANCE AGREEMENT",
            "This agreement is entered into by BigCorp and CleanSweep Facilities Services.",
            "CleanSweep will provide daily office cleaning and pantry maintenance for all floors.",
            "Contract term: July 1, 2025 to June 30, 2027.",
            "Monthly service retainer fee: $12,500.",
            "Emergency cleaning services will be billed at an hourly rate of $75."
        ],
        "description": "Scanned building facilities cleaning and maintenance service contract."
    }
]

for doc in scanned_pdfs:
    # First write a normal PDF
    temp_path = scanned_pdf_dir / f"temp_{doc['filename']}"
    create_text_pdf(temp_path, doc["title"], doc["lines"])
    
    # Convert it to scanned image-only PDF
    out_path = scanned_pdf_dir / doc["filename"]
    convert_to_scanned(temp_path, out_path)
    
    # Delete temporary file
    if temp_path.exists():
        temp_path.unlink()
        
    write_sidecar(out_path, {
        "title": doc["title"],
        "department": doc["department"],
        "access_level": doc["access_level"],
        "allowed_roles": doc["allowed_roles"],
        "allowed_users": [],
        "version": 1,
        "is_current_version": True,
        "source_trust_level": "official",
        "description": doc["description"]
    })

# ==========================================
# BATCH 3: Slack threaded conversations
# ==========================================
print("💬 Generating Batch 3: Slack Conversations...")

slack_threads = [
    {
        "filename": "engineering_pcs_incident.json",
        "channel": "engineering-incidents",
        "department": "ENGINEERING",
        "access_level": "DEPARTMENT",
        "allowed_roles": ["Software Engineer", "Administrator"],
        "messages": [
            {
                "id": "msg-slack-001",
                "author": "Anushka Jain",
                "text": "PCS is throwing 500s on checkout. Anyone else seeing this? PagerDuty just woke me up.",
                "timestamp": "2026-06-15T03:45:00Z",
                "replies": [
                    {
                        "id": "msg-slack-002",
                        "author": "Aarav Sharma",
                        "text": "Yeah, payments checkout service is failing. Looks like Redis is OOM and rejecting connection requests.",
                        "timestamp": "2026-06-15T03:48:00Z"
                    },
                    {
                        "id": "msg-slack-003",
                        "author": "Anushka Jain",
                        "text": "Aarav, good catch. I am going to purge the transient cart keys and restart the Redis cache cluster.",
                        "timestamp": "2026-06-15T03:52:00Z"
                    },
                    {
                        "id": "msg-slack-004",
                        "author": "Aarav Sharma",
                        "text": "Confirming the restart resolved the OOM. PCS checkout latency is back down to 35ms. Incident closed.",
                        "timestamp": "2026-06-15T04:10:00Z"
                    }
                ]
            }
        ],
        "description": "Slack incident thread detailing OOM issue on PCS Redis cluster and resolution."
    },
    {
        "filename": "hr_leave_payout.json",
        "channel": "hr-queries",
        "department": "HR",
        "access_level": "RESTRICTED",
        "allowed_roles": ["HR Manager", "Administrator"],
        "messages": [
            {
                "id": "msg-slack-101",
                "author": "Meera Kapoor",
                "text": "Quick question on leave payout: if an employee resigns, do we pay out unused carried-over leave days?",
                "timestamp": "2026-05-10T14:20:00Z",
                "replies": [
                    {
                        "id": "msg-slack-102",
                        "author": "Sarah Jenkins",
                        "text": "Yes, Meera. We pay out all accumulated standard leave and up to 5 days of carried-over leave at their current base rate.",
                        "timestamp": "2026-05-10T14:25:00Z"
                    },
                    {
                        "id": "msg-slack-103",
                        "author": "Meera Kapoor",
                        "text": "Got it. So if they carried over 5 days under the v2 policy, that gets added. If they have v1 carry-over (10 days), do we honor it?",
                        "timestamp": "2026-05-10T14:28:00Z"
                    },
                    {
                        "id": "msg-slack-104",
                        "author": "Sarah Jenkins",
                        "text": "No, v1 is fully superseded. Only up to 5 days of carry-over are legally honored for payout under the current v2 contract rules.",
                        "timestamp": "2026-05-10T14:32:00Z"
                    }
                ]
            }
        ],
        "description": "Slack HR discussion clarifying leave payout carry-over limits (5 days)."
    }
]

# We will generate 13 more simple threads to reach 15.
for idx in range(3, 16):
    slack_threads.append({
        "filename": f"general_chat_thread_{idx}.json",
        "channel": f"general-questions-{idx}",
        "department": "GENERAL",
        "access_level": "PUBLIC",
        "allowed_roles": [],
        "messages": [
            {
                "id": f"msg-gen-{idx}",
                "author": "Aarav Sharma",
                "text": f"What time does the third-floor cafeteria open in morning for breakfast?",
                "timestamp": "2026-07-01T08:30:00Z",
                "replies": [
                    {
                        "id": f"msg-gen-reply-{idx}",
                        "author": "Sarah Jenkins",
                        "text": "It opens at 8:00 AM and serves breakfast until 10:30 AM.",
                        "timestamp": "2026-07-01T08:35:00Z"
                    }
                ]
            }
        ],
        "description": f"General Slack thread number {idx} discussing operational topics."
    })

for thread in slack_threads:
    path = slack_dir / thread["filename"]
    # Write JSON data
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "channel": thread["channel"],
            "messages": thread["messages"]
        }, f, indent=2)
        
    write_sidecar(path, {
        "title": f"Slack Thread: #{thread['channel']}",
        "department": thread["department"],
        "access_level": thread["access_level"],
        "allowed_roles": thread["allowed_roles"],
        "allowed_users": [],
        "version": 1,
        "is_current_version": True,
        "source_trust_level": "informal",
        "description": thread["description"]
    })

# ==========================================
# BATCH 4: Excel and CSV files
# ==========================================
print("📊 Generating Batch 4: Spreadsheets...")

# 1. CSV files
csv_files = [
    {
        "filename": "finance_q1_q2_budget_report.csv",
        "department": "FINANCE",
        "access_level": "RESTRICTED",
        "allowed_roles": ["Finance Analyst", "Administrator"],
        "headers": ["Quarter", "Department", "Allocated Budget", "Spent Amount", "Status"],
        "rows": [
            ["Q1 2026", "Engineering", "2500000.00", "2450000.00", "Under Budget"],
            ["Q1 2026", "HR", "600000.00", "615000.00", "Over Budget"],
            ["Q1 2026", "Finance", "300000.00", "295000.00", "Under Budget"],
            ["Q2 2026", "Engineering", "2800000.00", "2750000.00", "Under Budget"],
            ["Q2 2026", "HR", "650000.00", "645000.00", "Under Budget"],
            ["Q2 2026", "Finance", "320000.00", "330000.00", "Over Budget"]
        ],
        "description": "Finance budget report showing Q1 and Q2 allocations and spending."
    },
    {
        "filename": "engineering_service_latencies.csv",
        "department": "ENGINEERING",
        "access_level": "DEPARTMENT",
        "allowed_roles": ["Software Engineer", "Administrator"],
        "headers": ["Service Name", "Average Latency (ms)", "P99 Latency (ms)", "Error Rate (%)", "Owner"],
        "rows": [
            ["Payment Checkout Service", "35.2", "98.5", "0.02", "Payments Platform Team"],
            ["User Profile Service", "12.5", "45.0", "0.01", "Identity Core Team"],
            ["Vector Search Indexer", "120.4", "350.2", "0.15", "Search & AI Team"],
            ["Audit Logger API", "8.2", "22.5", "0.00", "Security Engineering"]
        ],
        "description": "Core platform service operational latencies and error rates."
    },
    {
        "filename": "hr_salary_bands.csv",
        "department": "HR",
        "access_level": "RESTRICTED",
        "allowed_roles": ["HR Manager", "Administrator"],
        "headers": ["Grade Level", "Role Title", "Base Minimum", "Base Maximum", "Stock Options"],
        "rows": [
            ["L1", "Junior Software Engineer", "75000", "95000", "5000"],
            ["L2", "Software Engineer", "100000", "125000", "10000"],
            ["L3", "Senior Software Engineer", "130000", "160000", "20000"],
            ["L4", "Staff Software Engineer", "170000", "210000", "40000"],
            ["L5", "Principal Software Engineer", "220000", "280000", "80000"]
        ],
        "description": "HR grade level salary scales and standard equity allocations."
    },
    {
        "filename": "general_visitor_logs.csv",
        "department": "GENERAL",
        "access_level": "PUBLIC",
        "allowed_roles": [],
        "headers": ["Visitor Name", "Host Name", "Date", "Check-in Time", "Check-out Time", "Badge Issued"],
        "rows": [
            ["David Clark", "Anushka Jain", "2026-07-02", "09:15 AM", "01:30 PM", "V-880"],
            ["Emily Watson", "Meera Kapoor", "2026-07-02", "10:00 AM", "11:45 AM", "V-881"],
            ["Michael Chang", "Rohan Mehta", "2026-07-02", "02:00 PM", "04:30 PM", "V-882"]
        ],
        "description": "General office visitor logs and host mappings."
    }
]

for doc in csv_files:
    path = spreadsheet_dir / doc["filename"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(doc["headers"])
        writer.writerows(doc["rows"])
        
    write_sidecar(path, {
        "title": doc["filename"].replace("_", " ").replace(".csv", "").title(),
        "department": doc["department"],
        "access_level": doc["access_level"],
        "allowed_roles": doc["allowed_roles"],
        "allowed_users": [],
        "version": 1,
        "is_current_version": True,
        "source_trust_level": "official",
        "description": doc["description"]
    })

# 2. Excel multi-sheet files using openpyxl
excel_files = [
    {
        "filename": "finance_tax_brackets.xlsx",
        "department": "FINANCE",
        "access_level": "RESTRICTED",
        "allowed_roles": ["Finance Analyst", "Administrator"],
        "sheets": {
            "Federal Brackets": [
                ["Income Range Start", "Income Range End", "Tax Rate (%)"],
                ["0.00", "11600.00", "10.00"],
                ["11600.01", "47150.00", "12.00"],
                ["47150.01", "100525.00", "22.00"],
                ["100525.01", "191950.00", "24.00"]
            ],
            "State Surtaxes": [
                ["State", "Flat Rate (%)", "Luxury Surcharge (%)"],
                ["New York", "6.25", "1.50"],
                ["California", "8.00", "2.00"],
                ["Texas", "0.00", "0.00"],
                ["Florida", "0.00", "0.00"]
            ]
        },
        "description": "Multi-sheet financial tax rates for Federal income brackets and State surtaxes."
    },
    {
        "filename": "hr_employee_directory.xlsx",
        "department": "HR",
        "access_level": "PUBLIC",
        "allowed_roles": [],
        "sheets": {
            "Active Employees": [
                ["ID", "Name", "Email", "Department", "Date Hired"],
                ["user-001-aarav", "Aarav Sharma", "aarav.sharma@bigcorp.com", "General", "2023-04-12"],
                ["user-002-anushka", "Anushka Jain", "anushka.jain@bigcorp.com", "Engineering", "2024-06-01"],
                ["user-003-meera", "Meera Kapoor", "meera.kapoor@bigcorp.com", "HR", "2022-09-15"],
                ["user-004-rohan", "Rohan Mehta", "rohan.mehta@bigcorp.com", "Finance", "2021-11-20"]
            ],
            "Alumni": [
                ["ID", "Name", "Email", "Department", "Termination Date"],
                ["user-999-james", "James Bond", "james.bond@retired.com", "Security", "2025-12-31"]
            ]
        },
        "description": "BigCorp global employee directories split across Active and Alumni sheets."
    },
    {
        "filename": "leadership_board_voting_shares.xlsx",
        "department": "LEADERSHIP",
        "access_level": "CONFIDENTIAL",
        "allowed_roles": ["Administrator"],
        "sheets": {
            "Common Stock": [
                ["Shareholder", "Shares Owned", "Voting Power (%)"],
                ["Johnathan Miller", "5000000", "25.00"],
                ["Sarah Jenkins", "2000000", "10.00"],
                ["VentureCap Holdings", "8000000", "40.00"]
            ],
            "Preferred Stock": [
                ["Shareholder", "Preferred Shares Class", "Liquidation Preference"],
                ["VentureCap Holdings", "Class A-1", "1.5x"],
                ["Founder Trust", "Class Founders", "1.0x"]
            ]
        },
        "description": "Multi-sheet board shares ledger mapping common and preferred stock distributions."
    },
    {
        "filename": "engineering_depot_inventory.xlsx",
        "department": "ENGINEERING",
        "access_level": "DEPARTMENT",
        "allowed_roles": ["Software Engineer", "Administrator"],
        "sheets": {
            "Hardware Inventory": [
                ["Item Name", "Quantity", "Unit Cost", "Supplier"],
                ["MacBook Pro 16", "24", "2499.00", "Apple Inc."],
                ["Dell UltraSharp 32", "40", "899.00", "Dell Retail"],
                ["YubiKey 5 NFC", "150", "45.00", "Yubico US"]
            ],
            "Software Licenses": [
                ["License Name", "Seats Purchased", "Annual Cost", "Expiration Date"],
                ["IntelliJ IDEA", "50", "12500.00", "2027-01-30"],
                ["Slack Enterprise", "200", "48000.00", "2026-12-31"]
            ]
        },
        "description": "Engineering asset registers tracking hardware models and subscription software seats."
    }
]

for doc in excel_files:
    path = spreadsheet_dir / doc["filename"]
    from openpyxl import Workbook
    wb = Workbook()
    wb.remove(wb.active)
    
    for sheet_name, rows in doc["sheets"].items():
        ws = wb.create_sheet(title=sheet_name)
        for r in rows:
            ws.append(r)
            
    wb.save(str(path))
    
    write_sidecar(path, {
        "title": doc["filename"].replace("_", " ").replace(".xlsx", "").title(),
        "department": doc["department"],
        "access_level": doc["access_level"],
        "allowed_roles": doc["allowed_roles"],
        "allowed_users": [],
        "version": 1,
        "is_current_version": True,
        "source_trust_level": "official",
        "description": doc["description"]
    })

print("✨ All demo documents programmatically generated!")
