#!/bin/bash
# scripts/check_credentials.sh
# Run this BEFORE every pipeline to verify all credentials work.
# Usage: bash scripts/check_credentials.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$ROOT_DIR/.env"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  CREDENTIAL CHECK — $(date '+%Y-%m-%d %H:%M:%S')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── Load .env ──────────────────────────────────────────────────────
if [ -f "$ENV_FILE" ]; then
  set -a && source "$ENV_FILE" && set +a
  echo "  ✅ .env file found and loaded"
else
  echo "  ❌ .env file NOT found at: $ENV_FILE"
  echo "     Create it: cp .env.example .env  then fill in values"
  exit 1
fi

echo ""
echo "  ─── ENV VARS ────────────────────────────────────"

# GitHub
if [ -n "$GITHUB_TOKEN" ]; then
  echo "  ✅ GITHUB_TOKEN    = ${GITHUB_TOKEN:0:10}..."
else
  echo "  ❌ GITHUB_TOKEN    = NOT SET"
fi
if [ -n "$GITHUB_USERNAME" ]; then
  echo "  ✅ GITHUB_USERNAME = $GITHUB_USERNAME"
else
  echo "  ❌ GITHUB_USERNAME = NOT SET"
fi

# JIRA
if [ -n "$JIRA_URL" ]; then
  echo "  ✅ JIRA_URL        = $JIRA_URL"
else
  echo "  ❌ JIRA_URL        = NOT SET"
fi
if [ -n "$JIRA_USER" ]; then
  echo "  ✅ JIRA_USER       = $JIRA_USER"
else
  echo "  ❌ JIRA_USER       = NOT SET"
fi
if [ -n "$JIRA_TOKEN" ]; then
  echo "  ✅ JIRA_TOKEN      = ${JIRA_TOKEN:0:8}..."
else
  echo "  ❌ JIRA_TOKEN      = NOT SET"
fi

# Confluence
if [ -n "$CONFLUENCE_URL" ]; then
  echo "  ✅ CONFLUENCE_URL  = $CONFLUENCE_URL"
else
  echo "  ❌ CONFLUENCE_URL  = NOT SET"
fi
if [ -n "$CONFLUENCE_TOKEN" ]; then
  echo "  ✅ CONFLUENCE_TOKEN= ${CONFLUENCE_TOKEN:0:8}..."
else
  echo "  ❌ CONFLUENCE_TOKEN= NOT SET"
fi

echo ""
echo "  ─── LIVE API TESTS ──────────────────────────────"

# JIRA live test
if [ -n "$JIRA_URL" ] && [ -n "$JIRA_USER" ] && [ -n "$JIRA_TOKEN" ]; then
  AUTH=$(echo -n "$JIRA_USER:$JIRA_TOKEN" | base64)
  JIRA_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Basic $AUTH" \
    -H "Content-Type: application/json" \
    "$JIRA_URL/rest/api/2/myself" 2>/dev/null)
  if [ "$JIRA_STATUS" = "200" ]; then
    echo "  ✅ JIRA API        = HTTP 200 — authenticated"
    # Show accessible projects
    PROJECTS=$(curl -s \
      -H "Authorization: Basic $AUTH" \
      -H "Content-Type: application/json" \
      "$JIRA_URL/rest/api/2/project" 2>/dev/null | \
      python3 -c "import sys,json; d=json.load(sys.stdin); \
        [print(f'     - {p[\"key\"]}: {p[\"name\"]}') for p in d[:5]]" 2>/dev/null)
    echo "  📋 Accessible projects:"
    echo "$PROJECTS"
  else
    echo "  ❌ JIRA API        = HTTP $JIRA_STATUS — check JIRA_URL and JIRA_TOKEN"
  fi
else
  echo "  ⏭️  JIRA API test skipped — missing credentials"
fi

# Confluence live test
if [ -n "$CONFLUENCE_URL" ] && [ -n "$CONFLUENCE_USER" ] && [ -n "$CONFLUENCE_TOKEN" ]; then
  AUTH=$(echo -n "$CONFLUENCE_USER:$CONFLUENCE_TOKEN" | base64)
  CONF_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Basic $AUTH" \
    "$CONFLUENCE_URL/rest/api/space?limit=5" 2>/dev/null)
  if [ "$CONF_STATUS" = "200" ]; then
    echo "  ✅ Confluence API  = HTTP 200 — authenticated"
  else
    echo "  ❌ Confluence API  = HTTP $CONF_STATUS — check CONFLUENCE_URL and token"
  fi
else
  echo "  ⏭️  Confluence test skipped — missing credentials"
fi

# GitHub CLI
if command -v gh &>/dev/null; then
  if gh auth status &>/dev/null; then
    GH_USER=$(gh auth status 2>&1 | grep "Logged in" | grep -o "as .*" | cut -d' ' -f2)
    echo "  ✅ GitHub CLI      = authenticated as $GH_USER"
  else
    echo "  ❌ GitHub CLI      = not authenticated"
    echo "     Fix: source .env && gh auth login --with-token <<< \$GITHUB_TOKEN"
    # Auto-fix attempt
    if [ -n "$GITHUB_TOKEN" ]; then
      echo "     Attempting auto-fix..."
      echo "$GITHUB_TOKEN" | gh auth login --with-token 2>/dev/null
      if gh auth status &>/dev/null; then
        echo "  ✅ GitHub CLI      = auto-fixed — now authenticated"
      else
        echo "  ❌ GitHub CLI      = auto-fix failed — run manually"
      fi
    fi
  fi
else
  echo "  ❌ GitHub CLI      = gh not installed"
  echo "     Fix: brew install gh  (Mac)  OR  sudo apt install gh  (Linux)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Exit with error if any critical credential is missing
if [ -z "$GITHUB_TOKEN" ] || [ -z "$JIRA_URL" ] || [ -z "$CONFLUENCE_URL" ]; then
  echo "  ❌ One or more critical credentials missing — fix before running pipeline"
  exit 1
else
  echo "  ✅ All credentials loaded — ready to run pipeline"
  echo ""
fi
