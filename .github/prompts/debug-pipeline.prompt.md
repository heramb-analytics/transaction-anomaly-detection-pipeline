# Prompt: Debug Pipeline
# File: .github/prompts/debug-pipeline.prompt.md
# Use this prompt when a stage has failed and you want Copilot to diagnose and fix it.
# Type any of the trigger phrases below in Copilot Agent Mode.

## HOW TO USE

Type one of these in Copilot Chat (Agent Mode):

  debug pipeline
  fix pipeline error
  pipeline failed at stage {N}

Copilot will:
  1. Read the last error from logs/audit.jsonl
  2. Check which stage failed (from terminal output)
  3. Apply a targeted fix without re-running stages that already passed
  4. Resume from the failed stage

## WHAT THIS PROMPT ASKS COPILOT TO DO

### Step D-1 — Read logs
  Read logs/audit.jsonl — show the last 20 lines
  Read the terminal error (ask user to paste it if not visible)

### Step D-2 — Identify root cause
  Map the error to a source file using the stage-to-file table:
    Stage 1  → src/data/ingest.py
    Stage 2  → src/features/engineer.py, src/validation/checks.py
    Stage 3  → src/models/train.py
    Stage 4  → tests/unit/test_pipeline.py  (fix SOURCE, not test)
    Stage 5  → src/api/main.py
    Stage 6  → tests/e2e/test_api.py         (fix SOURCE, not test)
    Stage 7  → scripts/load_env.sh, git CLI
    Stage 8  → JIRA MCP (check credentials)
    Stage 9  → Confluence MCP (check credentials)
    Stage 10 → src/scheduler/nightly_job.py
    Stage 11 → scripts/generate_ppt.js

### Step D-3 — Apply fix
  Patch the identified source file.
  Re-run only that stage (not the full pipeline).
  If the fix requires re-running earlier stages: say so and ask user to confirm.

### Step D-4 — Verify
  After fix: run the minimal command that proves the stage works.
  Print: "✅ Stage {N} fixed — pipeline can resume"
  Print the command to resume from that stage.

## COMMON FIXES

  | Error                             | Likely Cause              | Fix                                      |
  |-----------------------------------|---------------------------|------------------------------------------|
  | AssertionError: Quality check N   | Bad data in raw file      | Check data/raw/ file, fix ingest.py      |
  | ModuleNotFoundError               | Missing pip package       | pip3 install {package} --break-system-packages |
  | FileNotFoundError: clean.parquet  | Stage 1 did not complete  | Re-run Stage 1                           |
  | JIRA 403 Forbidden                | Wrong token or no perms   | Check .env JIRA_TOKEN and JIRA_USER      |
  | Confluence 404                    | Wrong space key           | Run list_spaces via Confluence MCP       |
  | gh: not authenticated             | GitHub CLI token stale    | bash scripts/load_env.sh then re-auth    |
  | uvicorn: address in use           | API already running       | kill $(lsof -ti:8000)                    |
  | pptxgenjs not found               | npm package missing       | npm install -g pptxgenjs                 |
  | pytest 0 tests collected          | conftest.py missing       | Recreate tests/conftest.py with sys.path |
