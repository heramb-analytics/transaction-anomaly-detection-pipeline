# Prompt: Demo Mode — Explain the Pipeline Live
# File: .github/prompts/demo-mode.prompt.md
# Use this during demos to show stakeholders what each stage does without re-running everything.
# Type the trigger phrase in Copilot Chat (any mode).

## HOW TO USE

Type in Copilot Chat:

  demo mode
  explain the pipeline
  show what was built

Copilot will walk through each stage interactively, showing what was produced,
without re-running any code or making any API calls.

## WHAT COPILOT DOES IN DEMO MODE

Copilot presents a guided tour of the completed pipeline output:

### Tour Stop 1 — Architecture Overview
  Display the 12-stage flow diagram (ASCII art from the Confluence page).
  Explain what triggers the pipeline and how long it takes.

### Tour Stop 2 — The Dataset
  Read logs/quality_report.json.
  Say: "We started with {total_rows_before_cleaning} rows. After 10 automated quality
       checks, {total_rows_after_cleaning} clean rows were saved to clean.parquet."

### Tour Stop 3 — Features & EDA
  Read data/processed/feature_schema.json.
  Say: "{N} features were engineered automatically. Here are the top 5..."
  List top features by importance (from the schema file).
  Say: "5 EDA charts are in reports/figures/ — open to view."

### Tour Stop 4 — Model Performance
  Read models/pipeline_model_metrics.json.
  Present: algorithm, primary metric, all numeric metrics in a table.
  Say: "The model was selected by 3-fold CV grid search. No manual tuning."

### Tour Stop 5 — Live API
  Say: "The FastAPI dashboard is running at http://localhost:8000"
  Open http://localhost:8000 in a browser (using Playwright MCP or terminal: open http://localhost:8000)
  If browser cannot open: print the URL prominently and say "paste this in your browser."

### Tour Stop 6 — Test Results
  Say: "8 unit tests and 6 Playwright end-to-end browser tests all passed."
  List the 8 test names and their status.
  Say: "Screenshots of the live API are in reports/screenshots/"

### Tour Stop 7 — GitHub
  Print GITHUB_REPO_URL (from last pipeline run — read from logs/audit.jsonl if needed)
  Say: "All source code is committed and public. Clone it with:"
       git clone {GITHUB_REPO_URL}

### Tour Stop 8 — JIRA & Confluence
  Print JIRA_BOARD_URL and JIRA_EPIC_URL
  Print CONFLUENCE_PAGE_URL
  Say: "Tickets and documentation were created automatically — zero manual writing."

### Tour Stop 9 — The PowerPoint
  Say: "A 10-slide deck was generated at reports/pipeline_presentation.pptx"
  Say: "Open it with: open reports/pipeline_presentation.pptx"

### Tour Stop 10 — The Prompt
  Say: "Everything you just saw was triggered by typing two words: create pipeline"
  Print:
    ┌─────────────────────────────────────┐
    │  create pipeline                    │
    │                                     │
    │  That is the only prompt we typed.  │
    └─────────────────────────────────────┘

## DEMO TIPS
  - Keep the Copilot Chat panel visible during the demo.
  - Have http://localhost:8000 open in a browser tab before starting.
  - Have the reports/pipeline_presentation.pptx open in PowerPoint/Keynote.
  - The audit log (logs/audit.jsonl) shows every automated action — great for trust.
