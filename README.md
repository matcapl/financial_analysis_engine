# 📊 Financial Data Ingestion & Analysis Engine

This repo processes raw financial board pack data (Excel + PDF), ingests and stores it in a normalized PostgreSQL schema, calculates key metrics, generates structured questions, tracks updates, and flags changes.

---

## 🏗️ Structure

financial-data-repo/
├── .venv/ # Poetry-managed environment (ignored)
├── pyproject.toml # Python dependency & project metadata
├── requirements.txt # Exported from poetry (optional)
├── schema/
│ └── financial_schema.sql # PostgreSQL schema for financial DB
├── scripts/
│ ├── ingest_xlsx.py # Extract and load Excel files
│ ├── ingest_pdf.py # Extract and load PDFs with OCR
│ ├── calc_metrics.py # All transformations and KPIs
│ ├── questions_engine.py # Auto-generates checklist questions
│ └── update_ranking.py # Scoring, weighting, and audit trails
├── data/
│ └── sample_input.xlsx # Drop your raw files here
├── logs/
│ └── ingest_log.json # File source and versioning log
├── output/
│ └── final_scorecards.csv # Resulting data for board analysis
└── README.md

🧠 Features

Supports both monthly and quarterly financials (auto-sums & corroborates)
Stores actual, budget, and variance (both value & %)
Source traceability with document reference, page number, file hash
NLP-based question generation tied to thresholds
Scored, weighted checklists for board interrogation
Modular, extensible design — works across companies & rollups

🏗️ HOW EVERYTHING FLOWS TOGETHER

Ingestion → Derived Metrics → Live Questions → Logs → Reporting
[xlsx/pdf] 
  ↓
financial_metrics ←─── corroboration/source logging
  ↓
derived_metrics ←─── calc_metrics.py
  ↓
question_templates → live_questions ←─── questions_engine.py
                      ↓
                   question_logs
                      ↓
               generated_reports

🔄 VERSION TRACKING + WEIGHT EVOLUTION

Every change to a question’s weight, status, or score is logged
The current state is always the latest row in live_questions
Historical rank/score/weight = replay of question_logs
✅ This makes rollback, replays, or "simulate what was known on date X" feasible

🌱 Future Enhancements

Auto ingestion from email or cloud upload
Board-ready PDF summaries via headless browser
AI assistant integration (for commentary + followups)

⚖️ License

MIT — do with it what you will.

