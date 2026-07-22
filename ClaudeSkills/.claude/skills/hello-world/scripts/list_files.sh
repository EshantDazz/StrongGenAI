#!/usr/bin/env bash
# Dummy helper script for the hello-world skill.
# Prints the working directory and its top-level entries.
set -euo pipefail

echo "cwd: $(pwd)"
echo "top-level files:"
ls -1 .
