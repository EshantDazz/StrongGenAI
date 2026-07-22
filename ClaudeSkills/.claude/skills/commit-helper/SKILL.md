---
name: commit-helper
description: Draft a conventional-commit-style message for the current staged git changes. Use when the user runs /commit-helper, or asks for help writing a commit message.
---

# Commit Helper

Example of a skill that takes arguments and does real work with tools.

Arguments (`args`, optional): a short hint about the intent of the change, e.g. `/commit-helper fixes the login bug`. If omitted, infer intent from the diff alone.

When invoked:

1. Run `scripts/staged_summary.sh` to see a quick stat summary of what changed, then `git diff --staged` (fall back to `git diff` if nothing is staged) for the full detail.
2. If there are no changes at all, tell the user there's nothing to commit and stop.
3. Draft ONE commit message in Conventional Commits format (`type(scope): summary`), using `args` as a hint about intent if provided. See [references/conventional-commits.md](references/conventional-commits.md) for the type list and formatting rules.
4. Show the drafted message to the user. Do NOT run `git commit` yourself — just propose the message and let the user decide.
