# What actually cuts your AI token bill

If you've been using an AI coding agent for a while, you've probably had the moment where you check your usage and think: *where did all of that go?*

I've spent the last few months trying to find out. Here's what I actually learned.

---

## The biggest win isn't a cheaper model

My first instinct was to look for a smarter model configuration. Then a compression plugin. Then a different tool entirely. These things help, but I kept circling back to the same observation: most of the waste was happening before any tool could fix it. The agent was doing things I hadn't told it not to do.

The highest-leverage thing I found was the `AGENT.md` file — or `CLAUDE.md`, `AGENTS.md`, depending on your setup. Most people use it as a place to dump project context. It's also your best lever for controlling how the agent behaves when things go wrong.

**Loop caps matter more than they sound.** Adding a line like "cap each debug loop at 2-3 attempts, then stop and report" does more for token spend than most plugins. When an agent spins on a broken assumption, cost doesn't scale linearly — it compounds. Bad output fills the context window, reasoning degrades, the next output is worse. A two-line instruction in your config breaks that cycle before it starts.

**Pass only the signal, not the dump.** If you're feeding raw stack traces into context, you're paying for noise. Strip it down to the error type, the failing command, and the last relevant frame. That's what the agent needs. Everything else is overhead.

**Skills save re-explanation costs.** If you're re-explaining your project structure or conventions at the start of every session, you're paying for it each time. Encoding those as loadable skills means you teach once and reference forever.

---

## The tools I actually used

Once your config is reasonable, there's a useful layer on top.

**Graphify and Semble** both address the same problem: stopping the habit of dumping entire files into context. Graphify builds a semantic graph of your codebase so you can pull the relevant files rather than all of them. Semble does similar work at the search layer — lazy retrieval instead of pre-loading everything. Both are variations on the same idea: be surgical about what goes in, rather than comprehensive.

**Caveman** forces compressed output mode — the model writes less, explains less. I tested it across a few task types and the results were genuinely task-dependent:

| Task | Mode | Cost |
|---|---|---|
| Code review | Regular | $0.43 |
| Code review | Caveman | $0.46 |
| Code review | Caveman Ultra | $0.44 |
| File summary | Regular | $0.26 |
| File summary | Caveman Ultra | $0.09 |

On code review, it barely moves the needle or makes things marginally worse. On large summarisation tasks it cut costs by about 64%. The lesson isn't that Caveman is good or bad — it's that output compression only pays off when verbosity is actually the bottleneck.

**Ponytail** takes a different approach: instead of compressing output, it steers the agent toward writing less code in the first place. On backend tasks, this is mostly a good thing — the simplest working solution usually is the right one, and the token savings are real. On frontend work it gets more complicated. I asked it to implement a rating feature and it reached for a plain dropdown. Vanilla Claude built a custom component. The Ponytail version was cheaper. The vanilla version was better UI. Whether that trade-off works for you depends on what you're building.

---

## The honest summary

Configuration first, tools second. The fixes that cost nothing — loop caps, log preprocessing, reusable skills — consistently outperformed the plugins I tested, at least for the kinds of tasks I was running. The tools are useful at the margin, and some of them are genuinely impressive in the right context. But none of them rescue you from a runaway loop the way a two-line config instruction does.

---

*Sources:*
- *[Caveman](https://github.com/JuliusBrussee/caveman)*
- *[Caveman benchmarks](https://www.qwe.edu.pl/tutorial/caveman-claude-reduce-tokens-75-percent/)*
- *[Ponytail](https://medium.com/coding-nexus/ponytail-the-ai-plugin-that-makes-claude-code-write-54-less-code-without-breaking-anything-df29842c8ff6)*
- *[Graphify](https://github.com/Semble-AI/graphify)*
