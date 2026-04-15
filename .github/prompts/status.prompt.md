# Prompt: Pipeline Status Check
# File: .github/prompts/status.prompt.md
# Use this at any time to see what stages have completed and what artefacts exist.
# Type the trigger phrase in Copilot Chat (any mode).

## HOW TO USE

Type in Copilot Chat:

  pipeline status
  check pipeline
  what has been built

Copilot will check the filesystem and log files, then print a status dashboard
showing exactly which stages completed and which artefacts exist.

## WHAT COPILOT CHECKS

Run these shell commands and report results:

  # Core artefacts
  ls -lh data/raw/                                    → Stage 0 input
  ls -lh data/processed/clean.parquet 2>/dev/null     → Stage 1
  ls -lh data/processed/features.parquet 2>/dev/null  → Stage 2
  ls -lh data/processed/feature_schema.json 2>/dev/null
  ls -lh models/pipeline_model.pkl 2>/dev/null        → Stage 3
  ls -lh models/pipeline_model_metrics.json 2>/dev/null
  ls -lh logs/quality_report.json 2>/dev/null         → Stage 1
  ls -lh logs/validation_report.json 2>/dev/null      → Stage 2
  ls -lh reports/figures/0*.png 2>/dev/null           → Stage 2 (5 charts)
  ls -lh reports/screenshots/0*.png 2>/dev/null       → Stage 6 (6 screenshots)
  ls -lh reports/pipeline_presentation.pptx 2>/dev/null → Stage 11
  curl -s http://localhost:8000/health 2>/dev/null    → Stage 5 (API running?)
  tail -5 logs/audit.jsonl 2>/dev/null                → last 5 audit events

## STATUS DASHBOARD FORMAT

Print exactly this table (fill ✅ or ❌ based on artefact checks above):

  ┌──────────────┬────────────────────────────────┬────────┐
  │ Stage        │ Artefact                       │ Status │
  ├──────────────┼────────────────────────────────┼────────┤
  │ PRE-0 Creds  │ .env loaded                    │  ✅/❌ │
  │ Stage 0 Data │ data/raw/ has a file           │  ✅/❌ │
  │ Stage 1 Ingest│ clean.parquet                 │  ✅/❌ │
  │ Stage 2 Feats│ features.parquet               │  ✅/❌ │
  │ Stage 2 EDA  │ 5 charts in reports/figures/   │  ✅/❌ │
  │ Stage 3 Model│ pipeline_model.pkl             │  ✅/❌ │
  │ Stage 4 Tests│ (run pytest to verify)         │  ✅/❌ │
  │ Stage 5 API  │ http://localhost:8000 healthy  │  ✅/❌ │
  │ Stage 6 E2E  │ 6 screenshots exist            │  ✅/❌ │
  │ Stage 7 Git  │ (check audit.jsonl)            │  ✅/❌ │
  │ Stage 8 JIRA │ (check audit.jsonl)            │  ✅/❌ │
  │ Stage 9 Conf │ (check audit.jsonl)            │  ✅/❌ │
  │ Stage 10 Sched│ nightly_job.py exists         │  ✅/❌ │
  │ Stage 11 PPT │ pipeline_presentation.pptx     │  ✅/❌ │
  └──────────────┴────────────────────────────────┴────────┘

After the table, print:
  "To resume from the first ❌ stage: type  debug pipeline  in Chat."
  "To restart the full pipeline: type  create pipeline  in Chat."
