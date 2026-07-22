# Greeting Variants

Dummy reference file — shows how a skill can bundle extra docs that only get
read when actually needed, instead of stuffing everything into SKILL.md.

Pick a greeting style based on time of day if the user's local time is known:

| Time range | Greeting |
|------------|----------|
| 05:00–11:59 | "Good morning! Hello from the hello-world skill." |
| 12:00–17:59 | "Good afternoon! Hello from the hello-world skill." |
| 18:00–04:59 | "Good evening! Hello from the hello-world skill." |

If the time of day is unknown, default to the plain "Hello from the
hello-world skill!" greeting in SKILL.md.
