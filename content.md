# Five things that actually cut my AI token bill

**AI Coding Agents · Cost & Efficiency** · July 2026 · 10 min read

Notes from a few months of trying to reduce token spend on a real Java Spring Boot project — what helped, what didn't, and how the tools compared to the numbers on their marketing pages.

---

I've been running AI coding agents against the same Java Spring Boot codebase for a few months, mostly trying to figure out where the money was going. The usual suspects came up: pick a cheaper model, install a compression plugin, swap the code-search tool. Some of that worked. Some of it didn't. And a couple of the biggest savings came from things I hadn't been looking for.

What follows is a summary of what I tried, roughly ordered by how much it saved in practice. Two of the fixes are free. The other three cost something — either time to set up, or a tradeoff in output quality — and they're worth understanding before you install them.

---

## Loop caps in the config file

Loop caps turned out to matter more than I expected. When an agent gets stuck on a broken assumption, the failed attempts don't just cost you the failed calls — each one lands in the context window, and the next attempt tends to reason a little worse because of it. Over the course of a debugging session that isn't caught, this can compound into surprisingly large invoices.

The fix is a short instruction in `CLAUDE.md` (or `AGENT.md`, depending on your harness):

```
- Cap each debug loop at 2–3 attempts, then stop and report the blocker.
- Do NOT retry the same approach more than once. If something fails,
  form a new hypothesis before trying again.
- If an assumption cannot be verified with available tools, STOP and ask.
```

There's nothing sophisticated about it, but on the sessions where I would previously have lost a few dollars to a runaway loop, this consistently caught it before it got started. It's also worth noting that no compression tool can undo a loop after the fact — Caveman doesn't refund the tokens spent on twelve failed `npm run build`s — so this is one of the few interventions that has to happen before the spend, not after.

I ended up using two attempts as the cap for shell commands and three for anything involving reasoning about a new file. Beyond that, the agent tends to keep committing more confidently to the wrong direction rather than reconsidering.

---

## Preprocessing tool output before it hits the context window

A closely related pattern is being deliberate about what tools return to the agent. A four-thousand-line stack trace pasted verbatim into context is mostly noise, and the agent pays for the noise both on input and on the more confused output that tends to follow.

The version I've settled on is to strip logs down to three things before they reach the model:

- The error type
- The failing command
- The last relevant stack frame (usually the first frame from your own code)

This can be done in a bash wrapper, a pre-commit hook, or an MCP tool — the mechanism matters less than the principle. On a `mvn test` failure, this is often the difference between a 30k-token exchange and a 3k one, and I've found the agent's reasoning tends to be *better* on the shorter version, because it's not wading through Spring's reflection stack to locate the AssertionError.

The same idea applies to other tool calls that routinely produce large outputs. `git diff` is worth scoping by file. `ls` on large trees is worth capping. Web-scraped HTML is usually worth extracting to markdown first. In general, if a tool call regularly returns more than a screen of text, it's worth wrapping.

Neither of these two changes involves installing anything, and together they accounted for a larger share of my savings than any of the plugins below.

---

## Cheap models for the grunt work

The next thing worth checking is how your subagents are being sized. In Claude Code and most other harnesses, subagents inherit the parent's model by default. If you're on Opus and you fan out six agents to grep for callers of a function, all six of them are running on Opus rates for what is essentially a mechanical search task.

I added explicit model-selection rules in `CLAUDE.md` to handle this:

```
# Model selection
- File reading / code exploration subagents: use Haiku (claude-haiku-4-5)
- Implementation / reasoning subagents: inherit session model
- When in doubt, ask.
```

Claude Code's Explore agent is a good illustration of the pattern already built in — it's the read-only search agent, and it defaults to a faster, cheaper tier. The rule I've been applying is roughly: any subagent whose job is "go find X and tell me where it is" doesn't need to run on the largest model available.

The savings from this scale with how often you fan out. On research-heavy sessions where I was running lots of parallel searches, this cut around a fifth of my spend. On sessions that were mostly one agent writing code, it made no difference at all. It's a cheap change that pays where it applies.

---

## Snippet-level retrieval instead of whole-file reads

The most consistent source of avoidable spend in my logs was file reads. When the agent doesn't know which part of a 400-line file it needs, the natural default is to read the whole thing. Multiply that by twenty tool calls in a research task and it's straightforward to spend a couple hundred thousand input tokens on a question that has a five-line answer.

Two tools worth knowing about here are Graphify and Semble. They solve the same underlying problem — "return only the relevant slice" — in different ways. Graphify builds a semantic graph of the codebase, so you can query cross-file structure without having to read files. Semble does snippet-level retrieval: given a repository and a natural-language question, it returns the specific lines that answer it.

I ran the same three research questions on the Spring Boot codebase three ways: traditional grep-and-read, Graphify, and Semble.

| Method | Duration | Tool calls | Input tokens (est.) | Est. cost |
|---|---|---|---|---|
| Traditional grep + read | 163s | 25 | ~225k | ~$0.75 |
| Graphify | 81s | 11 | ~66k | ~$0.27 |
| Semble | 70s | 19 | ~76k | ~$0.33 |

Each of them had a distinct profile. Semble was the only one that answered every behavioral question fully correctly, because the snippet it returns tends to include enough of the method body for the agent to reason about what the code actually does. Graphify was the cheapest of the three and was noticeably stronger on questions about cross-file structure — which classes implement an interface, which handlers a message routes through. Traditional read still came out ahead when I already knew which file I was looking at; nothing beats knowing the path.

The workflow I settled on uses all three, roughly in this order:

1. Semble first for behavioral questions ("how does X work?", "where does Y get validated?").
2. Graphify when I need to map cross-file dependencies or find implementations.
3. A direct read when I already know the file.

The savings vary a lot by task. A well-scoped question with a known file gets essentially no benefit. A question like "how does the booking flow work?" can save 60–70% of the input tokens. Averaged across a week of real use, my input token usage dropped by roughly a third once I stopped defaulting to `Read`.

---

## Output compression: helpful in narrower cases than advertised

The last category is output-side tooling, and this is where the gap between what's advertised and what actually shows up in the numbers gets widest. I tried two tools that take quite different approaches.

### Caveman

[Caveman](https://github.com/JuliusBrussee/caveman) forces the model into a compressed output register — the "me code good, you run test" dialect that gives the tool its name. The marketing figure is around 75% savings. The JetBrains team measured it more carefully at [about 8.5% on real agent tasks](https://blog.jetbrains.com/ai/2026/07/speak-to-ai-agents-like-cavemen-tosave-tokens/), often erased by run-to-run variance.

My own results were more polarised than JetBrains's, in a way I think is worth explaining:

| Task | Mode | Cost | Wall time |
|---|---|---|---|
| Code review | Regular | $0.43 | 20m 27s |
| Code review | Caveman | $0.46 | 41m 46s |
| Code review | Caveman Ultra | $0.44 | 3m 18s |
| File summary | Regular | $0.26 | 1m 20s |
| File summary | Caveman Ultra | $0.09 | 39s |

On code review, Caveman was either roughly neutral or slightly worse, and Ultra mode saved wall time but not money — same token spend, faster clock. On file summarisation, it produced a genuine 64% cost cut. The reason for the split is that summarisation is a task where verbosity itself is the bottleneck; stripping verbosity is exactly what Caveman does. Code review, by contrast, is a task where the model's reasoning is the deliverable, and compressing the reasoning tends to make it worse rather than cheaper.

The heuristic I've been using is that if the model's prose is the deliverable, compression tends to help. If the model's code and reasoning are the deliverable, it tends not to. That means documentation, summarisation, and changelog generation are worth trying it on. Debugging, design, and code review generally aren't.

### Ponytail

[Ponytail](https://medium.com/coding-nexus/ponytail-the-ai-plugin-that-makes-claude-code-write-54-less-code-without-breaking-anything-df29842c8ff6) takes a different bet. Rather than compressing the format of the output, it constrains what the agent decides to build. The claim on the box is a 54% reduction in generated code. JetBrains [measured closer to 15%](https://blog.jetbrains.com/ai/2026/07/ponytail-skill-claude-tested/) — a real and statistically significant reduction, but roughly a third of what's advertised.

On small, well-scoped tasks, my own results converged:

| Task | Normal mode | Ponytail |
|---|---|---|
| Task 1 | 8 lines | 10 lines |
| Task 2 | 5 lines | 4 lines |
| Task 3 | 4 lines | 6 lines |
| **Total** | **17** | **20** |

Both modes were doing similar YAGNI reasoning on each task and landed in roughly the same place — Ponytail actually produced slightly more code overall on this set. The interesting behaviour showed up on a deliberately vague prompt: *"add a reporting system for sync stats."*

| Method | Lines | New abstractions | New files | Files modified |
|---|---|---|---|---|
| Ponytail | 3 | 0 | 0 | 1 |
| Normal | 163 | 4 | 4 | 8 |

Normal mode built a `SyncReport` record, a `SyncStatus` enum, a Spring component, and a REST endpoint — a coherent system, invented from a nine-word prompt. Ponytail added three log lines (sync start, employee count, sync complete with duration) and reasoned that per-operation logging already existed, so operators could grep for counts if they needed to.

Which of those is right depends entirely on what the user actually wanted, and that's the point. On ambiguous prompts, Ponytail defaults to the smallest interpretation, and Normal defaults to the most complete one. The savings show up where the prompts leave scope open, which is also why the measured benchmarks come in well below the advertised numbers — most real tasks aren't ambiguous. Ponytail tends to earn its keep when your prompts are vague or your team has a habit of over-building; on a codebase with clear conventions and specific tickets, the delta shrinks.

---

## Things I stopped doing

A few things I tried that didn't work out well enough to keep:

- **Aggressive per-call token limits.** Capping output at 4k tokens sounded prudent, but in practice it just caused the agent to hit the limit mid-thought and either fail or retry the whole call. The retries usually cost more than the limit saved.
- **Compression on reasoning tasks.** Caveman on code review was slower without being meaningfully cheaper. The model seems to need prose room to reason well.
- **Preloading "context" at session start.** Dumping an architecture doc into every session felt thorough, but most sessions didn't need most of the doc. Letting the agent pull what it needs via Semble or Graphify turned out to be leaner.

---

## Overall ranking

If I had to rank the five in rough order of how much they cut my bill, it would look something like this:

1. **Loop caps in config** — the single most useful change, and free.
2. **Preprocessing error logs and other large tool outputs** — free, and typically worth 20–40% of input tokens on debug-heavy sessions.
3. **Cheap models for grunt subagents** — free, worth 20–30% when you fan out, nothing when you don't.
4. **Snippet-level code search (Semble, Graphify)** — has a real setup cost, saved roughly a third of input tokens averaged across a week.
5. **Output compression (Caveman, Ponytail)** — task-dependent. Meaningful savings on summarisation and ambiguous prompts, neutral or worse elsewhere.

What's noticeably absent from the top of the list is model choice, harness swap, or the broader plugin ecosystem. Those matter, but in my experience they're small compared to whether the agent is allowed to spin on a broken assumption for fifteen turns. The configuration-level fixes were both the cheapest to apply and the most consistent in what they saved. The plugins are useful at the margins, and worth understanding, but they're the second pass, not the first.

---

## Sources & further reading

- [JetBrains: Does the Caveman skill really save 65% of tokens?](https://blog.jetbrains.com/ai/2026/07/speak-to-ai-agents-like-cavemen-tosave-tokens/) — the measured number is closer to 8.5%.
- [JetBrains: The Ponytail skill, tested](https://blog.jetbrains.com/ai/2026/07/ponytail-skill-claude-tested/) — closer to 15% than the advertised 54%.
- [Caveman on GitHub](https://github.com/JuliusBrussee/caveman)
- [Ponytail write-up (Coding Nexus)](https://medium.com/coding-nexus/ponytail-the-ai-plugin-that-makes-claude-code-write-54-less-code-without-breaking-anything-df29842c8ff6)
- [Caveman tutorial and benchmarks](https://www.qwe.edu.pl/tutorial/caveman-claude-reduce-tokens-75-percent/)
