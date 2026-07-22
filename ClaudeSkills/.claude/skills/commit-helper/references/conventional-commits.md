# Conventional Commits Cheat Sheet

Dummy reference file for the commit-helper skill.

## Format

```
type(scope): short summary

optional longer body
```

## Common types

| Type | When to use |
|------|-------------|
| feat | A new feature |
| fix | A bug fix |
| refactor | Code change that neither fixes a bug nor adds a feature |
| docs | Documentation only changes |
| test | Adding or correcting tests |
| chore | Tooling, deps, or config changes with no source impact |

## Rules of thumb

- Summary line under ~72 characters, imperative mood ("add", not "added").
- `scope` is optional — the module/directory most affected (e.g. `auth`, `parser`).
- Only include a body when the summary alone doesn't explain the *why*.
