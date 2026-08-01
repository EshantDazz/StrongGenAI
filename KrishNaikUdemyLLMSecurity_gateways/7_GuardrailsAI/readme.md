# Guardrails AI: Validators & On-Fail Actions

A practical guide to how Guardrails AI validates LLM inputs/outputs, and the five ways a failed validation can be handled: **Reask, Fix, Filter, Refrain, and Exception**.

---

## 1. What is a Validator?

A **validator** is the fundamental unit of a guardrail. It sits in the pipeline between a user and an LLM and enforces a rule against a piece of text — either before it reaches the LLM or after the LLM has generated a response.

```
User Input ──▶ [Input Validator] ──▶ LLM ──▶ Raw Output ──▶ [Output Validator] ──▶ Final Output
```

- **Input validator** – checks/cleans what the *user* sends to the LLM.
- **Output validator** – checks/cleans what the *LLM* sends back.

Both types work the same way internally: they take an input, apply some validation logic, and produce a **pass** or **fail** result — much like a test case. What happens next depends on the **on-fail action** configured for that validator (covered in detail below).

### Where Validators Come From

| Source | Description | Example Use Cases |
|---|---|---|
| **Guardrails Hub** | Pre-built, reusable validators maintained by Guardrails AI or the community — analogous to pulling a repo from GitHub | PII detection, competitor mentions, toxicity, hallucination/factual checks, jailbreak detection, JSON schema validation, SQL checks |
| **Custom Validators** | Written by you when the Hub doesn't already cover your specific business logic — analogous to building your own custom codebase | Company-specific disclaimers, refund policy caps, domain-specific business rules |

The Hub (`guardrails.ai/hub`) lets you search existing validators, see their description, intended use (input/output/both), and adoption stats before pulling one into your project.

---

## 2. Validators in Action (Demo Recap)

These examples come from a sample "NimbusPay" fintech support-bot demo used to illustrate validator behavior:

| Validator | What It Does | Example |
|---|---|---|
| **Detect PII** | Uses Microsoft's PII-detection approach to find personal information (card numbers, emails, etc.) and redacts it with placeholder tags | `"My card is 06XX..."` → `"My card is [CREDIT_CARD]"` |
| **Competitor Check** | Flags/removes mentions of a configured list of named competitors | `"Razorpay is also good"` → removed from output |
| **Toxicity** | Detects toxic/abusive language (via an LLM-as-judge in lightweight demo setups, since full toxicity models are memory-heavy) | Rude agent reply flagged with a toxicity score |
| **Restrict to Topic** | Confirms the text stays within an allowed topic domain (again via LLM-as-judge for lighter compute) | Off-topic request ("write me a poem about the ocean") flagged as out-of-topic |
| **Refund Disclaimer** *(custom)* | Appends a required legal/compliance disclaimer whenever a refund commitment is detected | `"We'll refund in 3 days"` → `"We'll refund in 3 days. All refunds are subject to verification."` |
| **Max Refund Claim** *(custom)* | Enforces a business rule/cap (e.g., auto-approve refunds under $100; anything above requires human sign-off) — catches LLM hallucinations that promise refunds beyond policy | LLM hallucinates a $4300 refund → validator blocks it, returns "over cap — needs human sign-off" |

---

## 3. On-Fail Actions

Once a validator runs, the result is either **pass** or **fail**.

- **Pass** → the output is returned as-is.
- **Fail** → the configured **on-fail action** determines what happens next.

Guardrails AI supports five on-fail actions: `reask`, `fix`, `filter`, `refrain`, and `exception`. This is documented directly in the Guardrails AI docs under **Concepts → On-Fail Actions**.

An important distinction:

> **`fix`, `filter`, `refrain`, and `exception` are deterministic fallbacks** — they act directly on the failed output using fixed logic.
> **`reask` is dynamic** — it goes back to the LLM with feedback and asks for a better answer.

### 3.1 Reask

**What it does:** Automatically generates feedback describing *why* validation failed, then re-prompts the LLM to regenerate a corrected response incorporating that feedback. The new response is validated again, and the cycle repeats up to a configured maximum number of iterations (e.g., 2 retries).

**Requires:** An active LLM/model context, since it involves a live re-call to the model.

**Example from the demo:**
- System prompt was deliberately misconfigured to have the bot repeat a customer's full card number verbatim.
- First LLM response leaked the card number → PII validator failed.
- Reask kicked in, fed back the validator's rejection reason, and the LLM regenerated a response like: *"I have confirmed that your card number ending in [last 4] is correct."* — no full number exposed.

**When to use it:** When you want the LLM itself to self-correct with guidance, rather than just patching the output mechanically.

---

### 3.2 Fix

**What it does:** Applies a **deterministic, validator-provided fix value** to the failed content instead of rejecting or re-prompting.

**Examples from the demo:**
- **Redact PII:** Card number replaced with `[CREDIT_CARD]` tag.
- **Refund Disclaimer (custom validator):** Whenever a refund promise is detected without the required legal disclaimer, the fix path automatically appends the missing disclaimer text.

**When to use it:** When there's a known, safe, static replacement or patch for the failure — no need to go back to the LLM.

---

### 3.3 Filter

**What it does:** Keeps only the **valid/structured parts** of the output and removes the invalid or offending fields/sentences — while still returning the rest of the content to the user.

**Example from the demo:**
- Input: *"I see the charge on card number [XXXX]. Your account is currently active and in good standing."*
- Output after filter: *"Your account is currently active and in good standing."*
- The offending sentence (containing the card number) is stripped out; everything else is delivered.

**Key distinction vs. Refrain:** Filter still **mandatorily returns output** to the user — just a cleaned-up version.

**When to use it:** When partial output is still useful and safe, and only specific offending fragments need to be removed.

---

### 3.4 Refrain

**What it does:** Fully **suppresses the output**. Nothing is released to the end user (or to the LLM, in the case of an input-side guardrail) — the response returned is empty or a safe placeholder, depending on output type.

**Example from the demo:**
- Same PII-laden input as above, but with `on_fail = refrain`.
- Result: an empty response — nothing is shipped, because *shipping nothing* is judged safer than shipping a redacted/filtered version.

**Key distinction vs. Filter:** Refrain returns **nothing**; Filter returns a **cleaned subset**.

**When to use it:** For higher-risk content where even a filtered version could be unsafe to expose.

---

### 3.5 Exception

**What it does:** Raises a proper **validation error** in code, halting the application flow entirely so the failure can be explicitly caught and handled by your own exception-handling logic.

**Example from the demo:**
- PII validator configured with `on_fail = exception`.
- On failure, the code raises an exception rather than returning any output — a hard stop.

**When to use it:** Reserved for **severe failures** where continuing execution at all would be unsafe — effectively the strictest, most conservative fallback.

---

## 4. Summary Table

| On-Fail Action | Behavior | Returns Output? | Involves LLM Re-call? | Best For |
|---|---|---|---|---|
| **Reask** | Re-prompts LLM with validator feedback, retries up to N times | Yes (regenerated) | ✅ Yes | Letting the LLM self-correct with guidance |
| **Fix** | Applies a deterministic, pre-defined fix/replacement | Yes (patched) | ❌ No | Known-safe, static corrections (e.g., redaction, appending disclaimers) |
| **Filter** | Removes only the offending fragment, keeps the rest | Yes (partial) | ❌ No | Partial content is still safe/useful |
| **Refrain** | Suppresses the output entirely | No (empty/safe default) | ❌ No | Content too risky to expose even partially |
| **Exception** | Raises a validation error, halts execution | No (error raised) | ❌ No | Severe failures requiring a hard stop |

---

## 5. Key Takeaways

- Validators are the **core building block** of any guardrail — they check input or output text against defined logic and return pass/fail.
- Use **Guardrails Hub validators** for common, reusable checks (PII, toxicity, competitor mentions, topic restriction, jailbreaks, schema/SQL checks).
- Write **custom validators** for business-specific rules not covered by the Hub (e.g., refund caps, mandatory disclaimers).
- On a **fail**, choose the on-fail action based on risk tolerance and desired behavior:
  - Want the LLM to try again with feedback? → **Reask**
  - Have a safe deterministic patch? → **Fix**
  - Only part of the output is problematic? → **Filter**
  - The whole output is too risky to release? → **Refrain**
  - The failure is severe enough to halt the app? → **Exception**

---

*Documentation compiled from a Guardrails AI walkthrough/demo covering validator mechanics and the `on_fail` action pipeline (Reask, Fix, Filter, Refrain, Exception).*