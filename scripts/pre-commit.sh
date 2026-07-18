#!/usr/bin/env bash
# Pre-commit hook — runs regression tests and stages the report.
# Installed by: bash scripts/install-hooks.sh

set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# Activate venv if present
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

echo ""
echo "🔍  Running regression tests before commit..."
echo ""

# Run tests
if python3 tests/run_tests.py; then
    # Tests passed — stage the updated report so it's included in the commit
    git add tests/test-report.md
    # Refresh the learner sync file for the Telegram digest (no-op if no state)
    if [ -f "data/state.json" ]; then
        python3 scripts/export_learner_sync.py && git add sync/learner.json
    fi
    exit 0
else
    echo ""
    echo "💡  Fix the failing tests, then commit again."
    echo "    To skip tests (not recommended): git commit --no-verify"
    echo ""
    exit 1
fi
