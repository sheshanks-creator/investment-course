#!/usr/bin/env bash
# Run this once after cloning to install the pre-commit hook.
# Usage: bash scripts/install-hooks.sh

set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOK_SRC="$REPO_ROOT/scripts/pre-commit.sh"
HOOK_DEST="$REPO_ROOT/.git/hooks/pre-commit"

cp "$HOOK_SRC" "$HOOK_DEST"
chmod +x "$HOOK_DEST"

echo "✅  Pre-commit hook installed at .git/hooks/pre-commit"
echo "    Tests will run automatically before every commit."
