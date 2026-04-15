# Prompt: Run Full Pipeline
# File: .github/prompts/run-pipeline.prompt.md
# This is the main trigger prompt.
# To start the full pipeline: type exactly "create pipeline" or "build pipeline" in Chat.
# Copilot reads copilot-instructions.md and runs all 12 stages automatically.

## HOW TO USE THIS PROMPT

1. Open VS Code in your project folder.
2. Open GitHub Copilot Chat (⌘I or Ctrl+I).
3. Make sure you are in **Agent Mode** (not Chat mode).
4. Type one of these exact phrases and press Enter:

   create pipeline
   build pipeline
   end to end pipeline

That is all. Copilot will run all 12 stages without stopping.

## WHAT HAPPENS AUTOMATICALLY

  Stage PRE-0 │ Credential check — JIRA, Confluence, GitHub verified
  Stage 0     │ Dataset discovery — problem type detected, columns understood
  Stage 1     │ Data ingestion — 10 quality checks → clean.parquet
  Stage 2     │ Feature engineering — features.parquet, 12 checks, 5 EDA charts
  Stage 3     │ Model training — algorithm selected, hyperparameter search, metrics saved
  Stage 4     │ Unit tests — 8 pytest tests, self-healing if any fail
  Stage 5     │ FastAPI + Dashboard — running at http://localhost:8000
  Stage 6     │ Playwright E2E tests — 6 tests, 6 screenshots
  Stage 7     │ GitHub push — README, requirements.txt, all files committed and pushed
  Stage 8     │ JIRA tickets — 1 Epic + 6 Stories created automatically
  Stage 9     │ Confluence page — 11-section page published automatically
  Stage 10    │ Scheduler — nightly retrain + drift detection configured
  Stage 11    │ PowerPoint — 10-slide deck saved to reports/pipeline_presentation.pptx
  Stage 12    │ Summary — all real links printed (GitHub, JIRA, Confluence, API)

## PREREQUISITES (run once before first pipeline)

  1. Copy and fill credentials:
       cp .env.example .env
       # Edit .env with your real values

  2. Verify credentials:
       bash scripts/check_credentials.sh

  3. Place your dataset:
       Copy your CSV or Parquet file into data/raw/
       Any file name is fine — Copilot will detect it automatically.

  4. Open Copilot in Agent Mode, then type: create pipeline

## EXPECTED DURATION
  ~25–40 minutes end-to-end depending on dataset size and hardware.
  All progress is printed in the Chat panel — no input needed from you.
