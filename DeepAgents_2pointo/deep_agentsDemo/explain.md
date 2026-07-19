# Why memory was empty (and how it got fixed)

## The rule
When you use `memory=["/projects/AGENTS.md"]`, the agent reads that file **only once per `thread_id`** and then caches the result in the checkpoint (`MemorySaver`).

- On a thread's **first** invoke → it reads `files=` and saves the memory.
- On **every later** invoke of the same thread → it skips reading and reuses the cached memory.

## Why the old cell failed
The thread `"default-demo-1"` had already been used earlier, *before* the file was seeded:

1. First invoke on that thread → no file present → memory saved as **empty `{}`**.
2. Your invoke on the same thread (now with `files=` seeded) → agent sees memory is "already loaded" (empty) → **skips reading your file** → prints `(No memory loaded)`.

So seeding the file too late does nothing — the thread was already "poisoned" with empty memory.

## Why the new cell works
Changed the thread to a **brand-new** `"mem-demo-fresh-1"`.

- Fresh thread → no cached memory yet → agent actually reads `files=`.
- The file is seeded in that same call → memory loads correctly ✅

## Remember
- Seed `files=` on the thread's **first** invoke.
- Re-running the same cell replays the cache → bump the suffix (`-2`, `-3`) each time.
- Want it to reload every time? Remove the `checkpointer=` argument — then there's no cache and every invoke re-reads the file.
