# Quick wins to stretch your AI budget

**AI Coding Agents · Cost & Efficiency** · July 2025 · 8 min read

Token-saving practices for AI coding agents — from configuration basics to tools with actual benchmark data behind them.

---

Let me set the scene: you're anxiously watching the progress bar on your monthly AI budget as your coding agent retries the same command-line action for the fifth time. "This time it'll work," you tell yourself.

A little while later, you're scratching your head as the agent you tasked with adding a simple new endpoint has produced a two-page design document detailing 15 steps. You let out a sigh and start coding it yourself.

If you've been using AI coding agents or assistants in the past six months, any of this should sound familiar. You've either made peace with it or — like me — been treating token spend as a solvable problem. Here's what actually moves the needle, with benchmark data where I have it.

---

## Most waste is a configuration problem.

### Fix your configuration first

I've been using my `CLAUDE.md` (or `AGENT.md`) configuration files mostly to enforce best-practices and to pass project specific context, but I was missing some pretty important rules. Let's run through some of them.

**Iteration caps.** The single highest-impact change was a hard limit on retry loops. An agent that has failed twice on the same approach is unlikely to succeed on the seventh attempt with the same strategy. Explicit rules prevent the compounding:

```
# In your AGENT.md / CLAUDE.md
- Cap each debug loop at 2–3 attempts, then stop and report the blocker.
- Do NOT retry the same approach more than once.
  If something fails, form a new hypothesis first.
- If an assumption cannot be verified with available tools, STOP and ask.
```

**Budget guardrails.** Adding spending limits to your specific agents could also avoid some unwanted surprises. I suggest limiting turns and cycles, but using hard caps on token usage could also work.

```
# In your AGENT.md / CLAUDE.md
Max Turns: 10
When reaching 10k output tokens, pause and escalate to the user.
Context should not exceed 150k tokens, else escalate to the user and ask.
```

**Error log preprocessing.** A 4,000-line stack trace passed verbatim into context is mostly noise. Stripping it down before it reaches the agent — error type, failing command, last relevant stack frame — reduces token spend per call and tends to improve reasoning quality.

- Error type only — not every repeated exception
- The failing command
- The last relevant stack frame

### Spawning six agents for a grep task? Use Haiku.

When using multiple agents, agents inherit the model of the parent or orchestrator — at least when using Claude Code. Having specific model selection criteria, either in `CLAUDE.md` or in your specific `Agent.md` files, is important.

Spawning 6 agents to read some code in batch should easily be done with the cheapest models.

```
# Model selection
- File reading / code exploration subagents: use claude-haiku-4-5 or newer (Haiku). Fast and cheap for navigation tasks.
- Implementation / reasoning subagents: inherit session model (Sonnet or above).
- When in doubt, ask user!
```

---

## Tools that actually help.

Most tools in this space promise savings without showing the work. These three have actual benchmark data behind them — which also means the data shows where they fail. I'll illustrate with A/B test results on a Java Spring Boot project.

### Code search: Graphify and Semble

Code searches are an inevitable part of most coding tasks. Loading entire files to answer questions about one function is one of the most common sources of avoidable token spend. Smarter retrieval fixes this without requiring any changes to the model or the agent framework.

Two rounds of testing compared Graphify and Semble against traditional grep+read across speed, token consumption, cost, and accuracy.

**Round 1: Graphify vs. traditional search**

| Method | Duration | Tool calls | Input tokens (est.) | Output tokens (est.) | Est. cost |
|--------|----------|------------|---------------------|----------------------|-----------|
| **Graphify** | 80.9s | 11 | ~66k | ~4,775 | ~$0.27 |
| Traditional | 163.4s | 25 | ~225k | ~5,300 | ~$0.75 |

*Round 1 — Graphify vs. traditional grep+read*

Graphify consumed roughly **3.4× fewer input tokens** and ran at half the wall-clock time. The cost delta was ~$0.27 vs ~$0.75 per research session. The accuracy picture was more nuanced:

| Question | Graphify | Traditional | Winner |
|----------|----------|-------------|--------|
| Q1 — UserRejected handler | Missed user.unsubscribe() and exception guard | Found both + ticketOption.remove(user) | Traditional |
| Q2 — Booking flow | High-level only, missed AggregateHandlers / double-dispatch | Full chain incl. @Order(1)/@Order(2) | Traditional |
| Q3 — AxxesUserSynchronizer | All 4 strategy implementations, correct | Named 1, inferred rest; correct | Graphify (breadth) |

| Dimension | Winner | Delta |
|-----------|--------|-------|
| Speed | Graphify | 2× faster |
| Input tokens | Graphify | ~3.4× fewer |
| Cost | Graphify | ~2.8× cheaper |
| Accuracy (method-level) | Traditional | Consistently deeper |
| Accuracy (breadth / relationships) | Graphify | Better at enumerating cross-file structure |

*Graphify wins on efficiency; traditional search wins on method-level behavioral detail*

Graphify's graph captures structural relationships well — "what depends on what", "which classes implement this interface". For questions that require reading what a method body actually does, traditional read still produces more complete answers.

**Round 2: three-way comparison — Traditional, Graphify, Semble**

| Method | Duration | Tool calls | Output chars | Input tokens (est.) | Output tokens (est.) | Est. cost |
|--------|----------|------------|--------------|---------------------|----------------------|-----------|
| **Traditional** | 58.1s | 11 | 20,500 | ~99k | ~5,125 | ~$0.37 |
| Graphify | 62.1s | 17 | 16,470 | ~85k | ~4,117 | ~$0.32 |
| **Semble** | 70.4s | 19 | 28,000 | ~76k | ~7,000 | ~$0.33 |

*Round 2 — Traditional, Graphify, Semble on the same task set*

Semble returns targeted snippets at the exact line rather than whole files, giving the lowest input token footprint while providing enough method-body context for accurate answers. It was the only tool to answer all behavioral questions fully correctly. Graphify was cheapest overall. Traditional search was fastest when the answer was in a known location.

| Dimension | Winner | Notes |
|-----------|--------|-------|
| Speed | Traditional | 58s vs 62s vs 70s — close, all fast |
| Input tokens | Semble | Snippet-level returns avoid large file reads |
| Cost | Graphify | Lowest combined in+out cost |
| Accuracy | Semble | Only tool to get Q1 and Q2 fully correct |
| Breadth (cross-file) | Semble / Graphify | Both surface relationship structure well |

*Overall verdict — each tool has a distinct profile*

> **Recommended workflow:** Semble for targeted behavioral questions → Graphify to map cross-file dependencies → traditional read only when you need the full file body.

### Output compression: Caveman

Caveman is a Claude Code plugin that forces the model into a compressed output mode — stripping responses to the functional minimum. The results are task-dependent, and the data is honest about that.

On a code review task, standard Caveman mode added cost and significantly increased wall time. Caveman Ultra recovered the time advantage but didn't reduce spend:

| Task | Mode | Cost | Wall time |
|------|------|------|-----------|
| Code review | Regular | $0.43 | 20m 27s |
| Code review | Caveman | $0.46 ▲ | 41m 46s ▲ |
| Code review | Caveman Ultra | $0.44 | 3m 18s ↓ |
| File summary | Regular | $0.26 | 1m 20s |
| **File summary** | **Caveman Ultra** | **$0.09 ↓ 64%** | **39s** |

*Caveman benchmark — task type determines whether compression helps or hurts*

The pattern: Caveman performs poorly on tasks where the model's reasoning and code output is the value. On summarisation tasks — where verbosity is the problem — Caveman Ultra saves significantly. Savings of up to 75% have been reported in specific setups.

### Output compression: Ponytail

Ponytail constrains the scope of what gets built rather than compressing the output format. The claim is a 54% reduction in generated code without breaking functionality. The tests tell a more specific story.

On concrete, well-scoped tasks, both modes produced nearly identical results — Ponytail wrote slightly more lines on the small task set, and normal mode was more accurate on method names:

| Method | Task 1 lines | Task 2 lines | Task 3 lines | Total lines | New abstractions |
|--------|--------------|--------------|--------------|-------------|------------------|
| **Normal** | 8 | 5 | 4 | **17** | 0 |
| Ponytail | 10 | 4 | 6 | 20 | 0 |

| Dimension | Winner | Notes |
|-----------|--------|-------|
| Line count | Normal | 17 vs 20 |
| Correctness | Normal | Found the real method name; Ponytail guessed |
| YAGNI reasoning | Ponytail | Explicitly surfaced what it chose not to do |
| Abstraction discipline | Tie | Both: 0 new abstractions |

*Small, concrete tasks — the methods converge*

Where the difference became dramatic was on a deliberately vague prompt: *"add a reporting system for sync stats."*

| Method | Lines of code | New abstractions | Files created | Files modified |
|--------|---------------|------------------|---------------|----------------|
| **Ponytail** | **3** | **0** | **0** | 1 |
| Normal | 163 | 4 | 4 | 8 |

*"Add a reporting system for sync stats" — scope interpretation diverges sharply*

**Ponytail — 3 lines of code.** Zero new abstractions. Zero new files. Reasoned that per-operation logging already existed in the action classes, so ops can grep for counts. Added three log lines: sync start, employee count, sync complete with duration.

**Normal mode — 163 lines of code.** 4 new types, 4 new files, 1 breaking interface change across all 4 implementors. Built a SyncReport record, SyncStatus enum, SyncReportStore Spring component, and a REST endpoint. A coherent system — interpreting the prompt more ambitiously than it was stated.

"Reporting system" is a scope magnet. Ponytail's value is most visible on tasks where an unconstrained interpretation would pull in types, stores, endpoints, and interface changes. On small, already-scoped tasks, the modes are functionally equivalent — and normal mode tends to find real method names more reliably.

### Head-to-head: Normal vs Ponytail vs Caveman

Run across the same three tasks: Ponytail wrote 11 lines total, Caveman 24, Normal 25. But Caveman cut prose output by 50% while barely touching code volume. Ponytail cut code by more than half while leaving prose roughly intact.

One task makes the distinction concrete: `isUserEnrolledInEducation`. Ponytail and Caveman both reached for `education.getEnrolledUsers().anyMatch(eu -> eu.is(user))` — leveraging the existing API. Normal routed through `bookingRepository.findAll()` and filtered in memory. That's not a style difference; it's a correctness difference.

On a logging task that was already solved, Ponytail produced zero lines. Normal added ten. Caveman recognised the work was done — and still wrote ten lines anyway.

Caveman's value is in the *communication layer* — same code as Normal, but half the prose, useful when output token cost matters across long sessions or high-volume agents. Ponytail's value is in the *decision layer* — it actively questions what to build, resulting in genuinely fewer lines and sharper scope calls. They're complementary: Ponytail + Caveman together would produce the tightest code with the most compressed explanation.

---

## Loops are the biggest cost driver.

The tools above all have genuine value in the right context. But the largest single lever — by a significant margin — is loop prevention.

A debugging loop that runs fifteen iterations on a broken assumption doesn't only waste 15× the tokens on those calls. It fills the context window with failed attempts, which degrades subsequent reasoning, which produces more iterations. The failure compounds. No compression tool reverses that after the fact.

What actually works, in rough order of impact:

1. **Hard iteration caps** — Two or three failed attempts at the same approach warrant a new hypothesis or a handoff to a human. This is the single largest source of runaway spend.

2. **Structured error preprocessing** — Summarise logs into structured facts before they enter the context window. Error type + immediate context only — the full dump adds noise without adding signal.

3. **Surgical code retrieval** — Semble or Graphify rather than whole-file reads. Retrieve what the task actually requires, not the entire module it lives in.

4. **Output compression on the right tasks** — Caveman Ultra for summarisation-heavy work where verbosity is the bottleneck. Ponytail for open-ended prompts where scope creep is the risk.

The model itself is rarely the bottleneck. Token spend scales with how the agent is orchestrated — how often it retries, how much context it loads, how much it produces per call.

---

## The loop cap is the only place to start

The biggest wins don't come from a library install. They come from iteration caps in `AGENT.md`, preprocessed error logs, and retrieval that's scoped to what the task actually needs. None of that is glamorous. It also doesn't show up in demos. It shows up on the invoice.

**Start with the loop cap. Everything else is secondary.**

---

## Sources & further reading

- [Caveman benchmarks and tutorial](https://www.qwe.edu.pl/tutorial/caveman-claude-reduce-tokens-75-percent/)
- [Caveman Mode — The New Stack](https://thenewstack.io/caveman-mode-token-savings/)
- [Ponytail — Coding Nexus](https://medium.com/coding-nexus/ponytail-the-ai-plugin-that-makes-claude-code-write-54-less-code-without-breaking-anything-df29842c8ff6)
- [Cutting LLM token costs with RTK — CodePointer](https://codepointer.substack.com/p/cutting-llm-token-costs-with-rtk)
- [Caveman — GitHub](https://github.com/JuliusBrussee/caveman)
