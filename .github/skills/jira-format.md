# JIRA Ticket Formatting Rules
# File: .github/skills/jira-format.md
# Copilot reads this before creating any JIRA tickets in Stage 8.

## Project Selection
Do NOT create a new JIRA project — requires admin rights most users don't have.
Instead:
  1. Call JIRA MCP: list_projects
  2. Pick the first project where the user has "Create Issues" permission
  3. Store as JIRA_PROJECT_KEY

## Epic Fields
  issuetype: Epic
  summary:   "{PROBLEM_TYPE} ML Pipeline — Automated v1.0"
  description: (use wiki markup — see template below)

## Story Fields (6 tickets inside the epic)
  issuetype: Story
  labels:    ["ml-pipeline", "automated", "copilot"]
  Each ticket must have a detailed description with:
    h3. What was done  (bullet list of actions)
    h3. Files created  (table: | File | Purpose |)
    h3. Results        (table: | Metric | Value |)

## Wiki Markup Rules
  Headers:        h1. h2. h3.
  Bold:           *bold text*
  Code inline:    {{code here}}
  Code block:     {code:language=python} ... {code}
  Table:          || Header || Header ||  then  | cell | cell |
  Bullet list:    * item
  Numbered list:  # item

## Ticket Summaries (use these exact formats)
  Epic:    "[PIPELINE] {PROBLEM_TYPE} ML Pipeline — End-to-End Automation v1.0"
  Stage 1: "[PIPELINE] Data Ingestion & Validation — {N}/10 quality checks passed"
  Stage 2: "[PIPELINE] Feature Engineering — {N} features + 5 EDA charts created"
  Stage 3: "[PIPELINE] Model Training — {ALGORITHM} {PRIMARY_METRIC}: {PRIMARY_VALUE}"
  Stage 5: "[PIPELINE] FastAPI + Dashboard deployed at http://localhost:8000"
  Stage 6: "[PIPELINE] 8 unit tests + 6 Playwright e2e tests — all passing"
  Stage 10:"[PIPELINE] Nightly scheduler — retrain + drift detection configured"

## After Creating Each Ticket
  Immediately capture the ticket KEY from the MCP response (e.g. TXAP-2).
  Print: "   🎫 Created: {KEY} — {summary}"
  Store each key: T1, T2, T3, T4, T5, T6

## After All Tickets
  JIRA_TICKETS_STR = comma-separated list of all ticket keys
  JIRA_BOARD_URL   = {JIRA_URL}/jira/software/projects/{JIRA_PROJECT_KEY}/boards
  JIRA_EPIC_URL    = {JIRA_URL}/browse/{JIRA_EPIC_KEY}
