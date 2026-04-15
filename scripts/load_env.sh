#!/bin/bash
# scripts/load_env.sh
# Sources .env file credentials into the current shell.
# Called by Stage 7 before any git/gh operations.
# Also callable manually: bash scripts/load_env.sh

ENV_FILE="$(cd "$(dirname "$0")/.." && pwd)/.env"

if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck source=/dev/null
  source "$ENV_FILE"
  set +a
  echo "   ✅ Credentials loaded from .env"
  echo "   ✅ JIRA_URL:        ${JIRA_URL:-NOT SET}"
  echo "   ✅ CONFLUENCE_URL:  ${CONFLUENCE_URL:-NOT SET}"
  echo "   ✅ GITHUB_TOKEN:    ${GITHUB_TOKEN:0:8}..."
else
  echo "   ❌ .env file not found at: $ENV_FILE"
  echo "   ℹ️  Create it: cp .env.example .env"
  echo "   ℹ️  Then fill in your real credential values"
  exit 1
fi
