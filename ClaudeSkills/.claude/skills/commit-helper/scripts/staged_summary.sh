#!/usr/bin/env bash
# Dummy helper script for the commit-helper skill.
# Prints a quick summary of staged changes (or unstaged, if nothing is staged).
set -euo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not inside a git repository."
  exit 1
fi

if git diff --cached --quiet; then
  echo "No staged changes — showing unstaged diff stat instead:"
  git diff --stat
else
  echo "Staged changes:"
  git diff --cached --stat
fi
