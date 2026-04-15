# Prompt: Run Pipeline on a New Dataset
# File: .github/prompts/new-dataset.prompt.md
# Use this to run the pipeline on a different CSV/Parquet file without rebuilding everything.
# Type the trigger phrase below in Copilot Agent Mode.

## HOW TO USE

  1. Copy your new CSV or Parquet file into data/raw/
  2. In Copilot Chat (Agent Mode) type:

       run pipeline on {filename}
       new dataset {filename}
       retrain on {filename}

  Copilot will run stages 0–3 (data → features → model) and then stages 7–11
  (push → JIRA → Confluence → PPT) using the new dataset.
  Stages 4–6 (tests + API) are re-verified automatically.

## WHAT COPILOT DOES

  Step 1 — Verify the file:
    ls -lh data/raw/{filename}
    Print: file size, extension, detected encoding

  Step 2 — Wipe previous run artefacts:
    rm -f data/processed/clean.parquet
    rm -f data/processed/features.parquet
    rm -f data/processed/feature_schema.json
    rm -f models/pipeline_model.pkl
    rm -f models/pipeline_model_metrics.json
    rm -f logs/quality_report.json
    rm -f logs/validation_report.json
    # Do NOT delete logs/audit.jsonl — keep full history

  Step 3 — Re-run stages in order:
    Stage 0  → discover new dataset (columns, problem type)
    Stage 1  → ingest new file, 10 quality checks, save clean.parquet
    Stage 2  → re-engineer features, 12 checks, 5 new EDA charts
    Stage 3  → retrain model on new data, save new metrics
    Stage 4  → re-run 8 unit tests (should all pass — self-heal if not)
    Stage 5  → restart API with new model (kill old uvicorn, restart)
    Stage 6  → re-run 6 Playwright e2e tests
    Stage 7  → git commit + push with message "retrain: new dataset {filename}"
    Stage 8  → update existing JIRA Epic; add new Story for retraining run
    Stage 9  → update existing Confluence page (or create v2 if update not possible)
    Stage 10 → scheduler remains configured — no change needed
    Stage 11 → regenerate PPT with new metrics and charts
    Stage 12 → print full summary with updated links

## NOTES
  - Do NOT place multiple files in data/raw/ — pick one per pipeline run.
  - The model file is overwritten. Previous .pkl is not backed up automatically.
  - JIRA Epic is reused — a new Story is added for this retraining run.
  - Confluence: if a page with the same title exists, it is updated (not duplicated).
