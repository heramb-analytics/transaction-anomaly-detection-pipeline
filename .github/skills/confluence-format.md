# Confluence Page Formatting Rules
# File: .github/skills/confluence-format.md
# Copilot reads this before creating the Confluence page in Stage 9.

## Page Location
  Space key:    CR  (or first available space if CR not found)
  Parent page:  ML Engineering  (create if not exists)
  Title:        "{PROBLEM_TYPE} ML Pipeline — v1.0"

## Required 11 Sections (in this order)

1. Executive Summary
   - 2-3 sentence overview of the problem and solution
   - Key result: algorithm + primary metric value
   - Table: GitHub link, API link, JIRA board link

2. Architecture
   - ASCII/text flow diagram showing all 12 stages
   - Use Confluence code macro with language: text

3. Data Catalogue
   - Table: Column | Type | Null% | Description
   - One row per column from clean.parquet

4. Feature Catalogue
   - Table: Feature | Type | How Computed | Importance
   - One row per feature from feature_schema.json

5. Model Card
   - Table: Attribute | Value
   - Rows: Algorithm, Train/Val/Test split, Data leakage check, Hyperparameter search
   - One row per metric from pipeline_model_metrics.json

6. API Reference
   - Table: Method | Path | Request Body | Response
   - All 4 endpoints: POST /predict, GET /health, GET /metrics, GET /

7. Dashboard Guide
   - Numbered steps: how to open dashboard, fill form, read results

8. Test Coverage
   - Table of all 8 unit tests with description and status
   - Table of all 6 e2e tests with screenshot reference

9. Screenshots
   - Bullet list of 6 screenshots with descriptions

10. How to Run
    - 3 code blocks: git clone, pip install, uvicorn start

11. Monitoring & Drift
    - Table: Job | Schedule | Trigger | Action
    - 2 rows: retrain job + drift check job
    - JIRA ticket reference for alerts

## Storage Format Rules
  Use Confluence HTML storage format (not wiki markup).
  Tables: <table><tbody><tr><th>...</th></tr><tr><td>...</td></tr></tbody></table>
  Code blocks: <ac:structured-macro ac:name="code">...</ac:structured-macro>
  Info panels: <ac:structured-macro ac:name="info">...</ac:structured-macro>

## After create_page Succeeds
  Extract URL from response in this priority order:
  1. response._links.webui  → prepend CONFLUENCE_URL
  2. response.url
  3. response.self
  4. CONFLUENCE_URL + "/pages/" + response.id
  Store as: CONFLUENCE_PAGE_URL
  Print immediately: "   🔗 {CONFLUENCE_PAGE_URL}"
