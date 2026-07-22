---
name: hello-world
description: Minimal example skill. Use when the user types /hello-world, or asks to test that skills are working.
---

# Hello World

This is the simplest possible skill — no arguments, no tools, just instructions.

When invoked:

1. Greet the user. For a time-of-day-appropriate variant, see [references/greetings.md](references/greetings.md) — otherwise just say "Hello from the hello-world skill!"
2. Run `scripts/list_files.sh` to report the current working directory and its top-level files.

Keep the response short — a few lines is enough. This skill exists purely to confirm that skill discovery and invocation are working end-to-end.
