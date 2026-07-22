
Insight - How to cut costs and stretch budgets

Outline: 
- intro 
- concepts and configuration to streamline usage
	- Agent.md config
		- avoid runaway loops 
		- budget guardrails
	- Skills
- Tools 
	- Input compression - reduce input tokens
		- headroom https://github.com/headroomlabs-ai/headroom
	- Code searching - reduce input tokens
		- Graphify
		- semble
		- ...
	- Output compression - reduce output tokens
		- Caveman https://github.com/JuliusBrussee/caveman
		- Ponytail
	- Complete agent harness 
		- Pi  https://pi.dev/
- Conclusion

  

biggest saver is usually not a cheaper model, it’s stopping bad loops early.
what’s worked for me:
- cap each debug loop at 2-3 attempts, then force a new hypothesis
- summarize logs into structured facts before giving them back to the agent
- pass only the failing command + last relevant stack trace, not the whole dump
- add a “stop if assumption is unverified” check
**Stop runaway loops before they compound:** Hard iteration caps at the orchestration layer. If an agent hasn't resolved after N attempts, halt and escalate to human review. This alone cuts the worst bleed.

**Budget guardrails at the agent level:** This is the part people skip. Setting per-agent spend limits means a runaway loop hits a ceiling and stops rather than you finding out on your invoice. Airia does this if you want something purpose-built for it.

**For error log bloat:** Preprocess before it hits the context window. Strip stack traces, repeated lines, timestamps and pass only the error type plus immediate context. Significant token reduction per call.



### Research 
1. Question and answer
2. Small coding task
3. Big and complex task

### Caveman
https://www.qwe.edu.pl/tutorial/caveman-claude-reduce-tokens-75-percent/

https://thenewstack.io/caveman-mode-token-savings/

Q&A 
Minimal savings. Simple Code Review task 
Regular: 
Total cost:            $0.4282
Total duration (API):  1m 57s
Total duration (wall): 20m 27s
Total code changes:    0 lines added, 0 lines removed
Usage by model:
    claude-haiku-4-5:  532 input, 12 output, 0 cache read, 0 cache write ($0.0006)
   claude-sonnet-4-6:  352 input, 5.9k output, 376.3k cache read, 60.2k cache write ($0.4276)
Caveman:
Total cost:            $0.4561
Total duration (API):  1m 56s
Total duration (wall): 41m 46s
Total code changes:    0 lines added, 0 lines removed
Usage by model:
    claude-haiku-4-5:  532 input, 12 output, 0 cache read, 0 cache write ($0.0006)
   claude-sonnet-4-6:  427 input, 5.3k output, 490.3k cache read, 60.6k cache write ($0.4555)

Caveman Ultra:
Total cost:            $0.4378
Total duration (API):  1m 39s
Total duration (wall): 3m 18s
Total code changes:    0 lines added, 0 lines removed
Usage by model:
   claude-sonnet-4-6:  17 input, 5.1k output, 426.8k cache read, 62.1k cache write ($0.4372)
    claude-haiku-4-5:  532 input, 14 output, 0 cache read, 0 cache write ($0.0006)


Summarize files and list todo's
Regular:
Total cost:            $0.2617
Total duration (API):  33s
Total duration (wall): 1m 20s
Total code changes:    0 lines added, 0 lines removed
Usage by model:
    claude-haiku-4-5:  532 input, 16 output, 0 cache read, 0 cache write ($0.0006)
   claude-sonnet-4-6:  348 input, 1.2k output, 148.7k cache read, 52.7k cache write ($0.2611)

Caveman ultra:
Total cost:            $0.0936
Total duration (API):  27s
Total duration (wall): 39s
Total code changes:    0 lines added, 0 lines removed
Usage by model:
    claude-haiku-4-5:  532 input, 16 output, 0 cache read, 0 cache write ($0.0006)
   claude-sonnet-4-6:  5 input, 1.1k output, 139.6k cache read, 9.2k cache write ($0.0930)

## Graphify
A/B Test Round 2 — Full Comparison

Speed

┌─────────────┬──────────┬────────────┐
│   Method    │ Duration │ Tool Calls │
├─────────────┼──────────┼────────────┤
│ Graphify    │ 80.9s    │ 11         │
├─────────────┼──────────┼────────────┤
│ Traditional │ 163.4s   │ 25         │
└─────────────┴──────────┴────────────┘

Graphify is 2× faster. Traditional search reads whole files sequentially and accumulates more context per iteration, which costs time.

---
Token Input / Output (estimated)

Token counts aren't directly observable from inside agents, so these are estimates based on call count × average context size per call, and output chars ÷ 4.

┌─────────────┬─────────────────────┬──────────────────────┬──────────────┐
│   Method    │ Input tokens (est.) │ Output tokens (est.) │ Output chars │
├─────────────┼─────────────────────┼──────────────────────┼──────────────┤
│ Graphify    │ ~66k                │ ~4,775               │ 19,100       │
├─────────────┼─────────────────────┼──────────────────────┼──────────────┤
│ Traditional │ ~225k               │ ~5,300               │ 21,200       │
└─────────────┴─────────────────────┴──────────────────────┴──────────────┘

Traditional consumes roughly 3.4× more input tokens — file reads are verbose, and context compounds across calls.

---
Cost (estimated, Sonnet pricing $3/$15 per MTok in/out)

┌─────────────┬────────────────┐
│   Method    │ Estimated cost │
├─────────────┼────────────────┤
│ Graphify    │ ~$0.27         │
├─────────────┼────────────────┤
│ Traditional │ ~$0.75         │
└─────────────┴────────────────┘

Traditional is ~2.8× more expensive per research session.

---
Accuracy

┌───────────────────────┬──────────────────────────────────┬─────────────────────────────┬─────────────┐
│       Question        │             Graphify             │         Traditional         │   Winner    │
├───────────────────────┼──────────────────────────────────┼─────────────────────────────┼─────────────┤
│                       │ Missed user.unsubscribe() and    │ Correctly found both, plus  │             │
│ Q1 — UserRejected     │ the                              │ ticketOption.remove(user)   │ Traditional │
│ handler               │ AggregateDoesNotExistException   │ detail                      │             │
│                       │ guard                            │                             │             │
├───────────────────────┼──────────────────────────────────┼─────────────────────────────┼─────────────┤
│                       │ Correct high-level flow, missed  │ Full class-by-class chain   │             │
│ Q2 — Booking flow     │ AggregateHandlers /              │ including                   │ Traditional │
│                       │ double-dispatch detail           │ @Order(1)/@Order(2)         │             │
│                       │                                  │ parallel handlers           │             │
├───────────────────────┼──────────────────────────────────┼─────────────────────────────┼─────────────┤
│ Q3 —                  │ Named all 4 strategy             │ Named 1 implementation then │ Graphify    │
│ AxxesUserSynchronizer │ implementations, correct         │  inferred rest; correct     │ (breadth)   │
│                       │ conclusion                       │ conclusion                  │             │
└───────────────────────┴──────────────────────────────────┴─────────────────────────────┴─────────────┘

---
Summary

┌────────────────────────────────────┬─────────────┬────────────────────────────────────────────┐
│             Dimension              │   Winner    │                   Delta                    │
├────────────────────────────────────┼─────────────┼────────────────────────────────────────────┤
│ Speed                              │ Graphify    │ 2× faster                                  │
├────────────────────────────────────┼─────────────┼────────────────────────────────────────────┤
│ Input tokens                       │ Graphify    │ ~3.4× fewer                                │
├────────────────────────────────────┼─────────────┼────────────────────────────────────────────┤
│ Cost                               │ Graphify    │ ~2.8× cheaper                              │
├────────────────────────────────────┼─────────────┼────────────────────────────────────────────┤
│ Accuracy (method-level detail)     │ Traditional │ Consistently deeper                        │
├────────────────────────────────────┼─────────────┼────────────────────────────────────────────┤
│ Accuracy (breadth / relationships) │ Graphify    │ Better at enumerating cross-file structure │
└────────────────────────────────────┴─────────────┴────────────────────────────────────────────┘

Verdict: Graphify wins decisively on efficiency (speed, cost, token consumption) but loses on depth for method-level behavioral questions. It's the right tool for "what depends on what", "which classes implement this interface", and broad architectural orientation. Traditional grep+read is still necessary when you need to know exactly what a method body does — Graphify's graph captures structure, not semantics. The ideal workflow is Graphify first to navigate, traditional read to confirm.

----------
A/B/C Test Results: Traditional vs Graphify vs Semble

Speed & Efficiency

┌─────────────┬──────────┬────────────┬──────────────┐
│   Method    │ Duration │ Tool Calls │ Output Chars │
├─────────────┼──────────┼────────────┼──────────────┤
│ Traditional │ 58.1s    │ 11         │ 20,500       │
├─────────────┼──────────┼────────────┼──────────────┤
│ Graphify    │ 62.1s    │ 17         │ 16,470       │
├─────────────┼──────────┼────────────┼──────────────┤
│ Semble      │ 70.4s    │ 19         │ 28,000       │
└─────────────┴──────────┴────────────┴──────────────┘

Traditional was fastest this round — notably it also used the fewest tool calls (11 vs 17/19). This is because traditional grep/read can be very efficient when you know exactly what file to look at, while Graphify and Semble require iterative querying to navigate.

---
Token & Cost Estimates (Sonnet pricing, $3/$15 per MTok in/out)

┌─────────────┬─────────────────────┬──────────────────────┬────────────────┐
│   Method    │ Input tokens (est.) │ Output tokens (est.) │ Estimated cost │
├─────────────┼─────────────────────┼──────────────────────┼────────────────┤
│ Traditional │ ~99k                │ ~5,125               │ ~$0.37         │
├─────────────┼─────────────────────┼──────────────────────┼────────────────┤
│ Graphify    │ ~85k                │ ~4,117               │ ~$0.32         │
├─────────────┼─────────────────────┼──────────────────────┼────────────────┤
│ Semble      │ ~76k                │ ~7,000               │ ~$0.33         │
└─────────────┴─────────────────────┴──────────────────────┴────────────────┘

Semble has the lowest input token footprint (returns targeted snippets, not whole files), but its higher output char count (28k — verbose snippet context) keeps cost roughly on par with Graphify. Graphify is cheapest overall at ~$0.32.

---
Accuracy

Question: Q1 — UserRejected handler
Traditional: ✅ user.unsubscribe(), exception guard
Graphify: ❌ Missed user.unsubscribe(), only found booking.updated()
Semble: ✅ booking.reject(user), exception guard, commit reference
Best: Semble
────────────────────────────────────────
Question: Q2 — Booking flow
Traditional: ✅ Good chain, missed BookingsViewManager
Graphify: ⚠️ High-level, missed AggregateHandlers/EventStorePublisher steps
Semble: ✅ Full class chain incl. DynamodbEventStore, BookingsViewManager, double-dispatch
Best: Semble
────────────────────────────────────────
Question: Q3 — AxxesUserSynchronizer
Traditional: ✅ All 4 actions, correct conclusion
Graphify: ✅ All 4 actions, correct conclusion
Semble: ✅ All 4 actions, correct conclusion
Best: Tie

---
Overall Verdict

┌──────────────────────┬───────────────────────┬──────────────────────────────────────────────┐
│      Dimension       │        Winner         │                    Notes                     │
├──────────────────────┼───────────────────────┼──────────────────────────────────────────────┤
│ Speed                │ Traditional           │ 58s vs 62s vs 70s — close, all fast          │
├──────────────────────┼───────────────────────┼──────────────────────────────────────────────┤
│ Input tokens         │ Semble                │ Snippet-level returns avoid large file reads │
├──────────────────────┼───────────────────────┼──────────────────────────────────────────────┤
│ Cost                 │ Graphify              │ Lowest combined in+out cost                  │
├──────────────────────┼───────────────────────┼──────────────────────────────────────────────┤
│ Accuracy             │ Semble                │ Only tool to get Q1 and Q2 fully correct     │
├──────────────────────┼───────────────────────┼──────────────────────────────────────────────┤
│ Breadth (cross-file) │ Tie (Semble/Graphify) │ Both surface relationship structure well     │
└──────────────────────┴───────────────────────┴──────────────────────────────────────────────┘

Key finding: Semble is the most accurate tool — it returns actual code snippets at the right line, giving the agent enough method-body detail to answer behavioral questions correctly, while avoiding the full-file verbosity of traditional read. Graphify is fastest to navigate structurally but loses on behavioral accuracy because its graph captures relationships, not code semantics. Traditional search remains competitive on speed when the searcher knows where to look, but accuracy varies by experience.

Recommended workflow: Semble for targeted behavioral questions → Graphify to map cross-file dependencies → Traditional read only when you need the full file context.


## PONYTAIL
A/B Test: Normal vs Ponytail

Quantitative

┌──────────┬──────────────┬──────────────┬──────────────┬─────────────┬──────────────────┐
│  Method  │ Task 1 lines │ Task 2 lines │ Task 3 lines │ Total lines │ New abstractions │
├──────────┼──────────────┼──────────────┼──────────────┼─────────────┼──────────────────┤
│ Normal   │ 8            │ 5            │ 4            │ 17          │ 0                │
├──────────┼──────────────┼──────────────┼──────────────┼─────────────┼──────────────────┤
│ Ponytail │ 10           │ 4            │ 6            │ 20          │ 0                │
└──────────┴──────────────┴──────────────┴──────────────┴─────────────┴──────────────────┘

Ponytail wrote 3 more lines than normal. Both introduced zero new abstractions.

---
Qualitative Differences

Task 1 — GET /bookings/count
- Both reached the same solution. Normal returned long, Ponytail returned int. Ponytail explicitly called out it skipped a DTO wrapper — but normal never considered one either.

Task 2 — isUserEnrolled check
- Normal found the actual method name user::isEnrolledFor (verified at User.java:194). Ponytail used user::isSubscribedTo — which may be wrong. Normal wins on correctness here.
- Both used a 1-liner stream, same structure.

Task 3 — Logging
- Normal: clean 4-line solution using existing variable names already in scope.
- Ponytail: 6 lines, suggested changing addUsers/deleteUsers return types to int to get counts — then explicitly said it skipped changing the UserSynchronizationAction interface. It avoided the interface change but still touched more code than necessary.

---
Verdict

┌────────────────────────┬──────────┬──────────────────────────────────────────────┐
│       Dimension        │  Winner  │                    Notes                     │
├────────────────────────┼──────────┼──────────────────────────────────────────────┤
│ Line count             │ Normal   │ 17 vs 20                                     │
├────────────────────────┼──────────┼──────────────────────────────────────────────┤
│ Correctness            │ Normal   │ Found the real method name; Ponytail guessed │
├────────────────────────┼──────────┼──────────────────────────────────────────────┤
│ YAGNI reasoning        │ Ponytail │ Explicitly surfaced what it chose not to do  │
├────────────────────────┼──────────┼──────────────────────────────────────────────┤
│ Abstraction discipline │ Tie      │ Both: 0 new abstractions                     │
└────────────────────────┴──────────┴──────────────────────────────────────────────┘

Finding: For well-scoped, concrete tasks in a codebase with clear patterns, Ponytail and normal coding converge on nearly identical solutions. Ponytail's distinctive value — the explicit "what I chose NOT to do" reasoning — is most useful when a task is vague or could balloon into over-engineering. On small, already-minimal tasks like these, it doek against, and can slightly overshoot bytrying to restructure things (Task 3 ret itself.

Ponytail would likely show a clearer win a reporting system for sync stats" or"build a booking analytics dashboard" — ded and an unconstrained developer might
reach for abstractions.


---
A/B Test: "Add a reporting system for sync stats"

Quantitative

┌──────────┬───────────────┬──────────────────┬───────────────┬────────────────┐
│  Method  │ Lines of code │ New abstractions │ Files created │ Files modified │
├──────────┼───────────────┼──────────────────┼───────────────┼────────────────┤
│ Ponytail │ 3             │ 0                │ 0             │ 1              │
├──────────┼───────────────┼──────────────────┼───────────────┼────────────────┤
│ Normal   │ 163           │ 4                │ 4             │ 8              │
└──────────┴───────────────┴──────────────────┴───────────────┴────────────────┘

54× more code from the normal coder. 4 new types vs none.

---
What normal built

- ActionSyncStats record — return type for each action
- SyncStatus enum — SUCCESS/FAILURE
- SyncReport record — wraps timing, employee count, per-action stats
- SyncReportStore Spring component — volatile in-memory field
- Changed the UserSynchronizationAction interface return type (breaking change to all 4 implementors)
- New REST endpoint GET /debug/users/_sync/report
- New test cases

It's a coherent, well-reasoned system. The interface change is the real cost — it touches 4 implementors and changes a contract.

What Ponytail built

3 log lines: sync start, employee count fetched, sync complete with duration. Noted that per-operation logs already existed in the action classes, so grep already gives you counts.

What Ponytail explicitly refused to build

SyncReport record, SyncReporter interface, Actuator/Micrometer metrics, REST endpoint, email/Slack notification, sync history persistence, interface return-type change — with the reasoning: "individual add/delete operations are already logged by the existing actions, so ops can grep counts."

---
Verdict

┌───────────────────────────┬──────────┬───────────────────────────────────────────────────────────────┐
│         Dimension         │  Winner  │                             Notes                             │
├───────────────────────────┼──────────┼───────────────────────────────────────────────────────────────┤
│ Minimal viable solution   │ Ponytail │eed                                  │
├───────────────────────────┼──────────┼───────────────────────────────────────────────────────────────┤
│ Queryable by ops          │ Tie      │al: REST endpoint                    │
├───────────────────────────┼──────────┼───────────────────────────────────────────────────────────────┤
│ Correctness of            │ Ponytail │ogs already cover detail             │
│ scope-check               │          │                                                               │
├───────────────────────────┼──────────┼─────────────────────────────────────┤
│ Extensibility             │ Normal   │ Clean typed model if you later need dashboards, alerting,     │
│                           │          │                                     │
├───────────────────────────┼──────────┼───────────────────────────────────────────────────────────────┤
│ Risk                      │ Ponytail │nterface — breaks all 4 implementors │
└───────────────────────────┴──────────┴───────────────────────────────────────────────────────────────┘  
This is the test case where Ponytail's philosophy has clear value. "Reporting system" is a scope magnet — it pulls in types, stores, endpoints, anly. Ponytail short-circuited all of thatby asking the real question: what does ops actually need to see? The answer was: a log line with counts and duration. That's 3 lines. The normal solut solves a more ambitiousinterpretation of the task than was asked for.

## Sources
https://warden.sentry.dev/benchmarking - PI vs Claude harness
https://medium.com/coding-nexus/ponytail-the-ai-plugin-that-makes-claude-code-write-54-less-code-without-breaking-anything-df29842c8ff6 - Ponytail


https://codepointer.substack.com/p/cutting-llm-token-costs-with-rtk
https://www.skillsbench.ai/?utm_source=the+new+stack&utm_medium=referral&utm_content=inline-mention&utm_campaign=tns+platform




Single pass - Sonnet 4.6
No prior notes or knowledge files — I'll work directly from your research and my own knowledge. Let me also do a quick supplementary scan for any tools mentioned.
Good, no conflicting priors. Let me write this up now — using your intro, your research data, and my own knowledge to fill in the gaps.

---

# Stop Burning Money: Token-Saving Practices (and the Tools That Actually Help)

---

## The Context Window is Not a Landfill

You're anxiously watching the progress bar on your monthly AI budget allocation as your favorite little buddy tries the same command line action for the 5th time. *This time he's gonna get it right*, you think to yourself.

A little while later you're scratching your head as the agent you tasked with implementing a simple new endpoint generates a two-page design document describing the 15 steps needed. You let out a sigh and start implementing yourself.

If you've been using AI coding agents in the past six months, this should sound familiar. And you've either accepted this as the price of the future, or — like me — have been desperately trying to stretch that precious token budget before your VP of Engineering notices the AWS bill.

In this post, I'll share some hard-won insights, configuration tricks, and a handful of tools that'll make your coding buddy last a little longer — without making it dumber. Let's go.

---

## Part 1: Before You Install Anything — Fix Your Configuration

Here's the uncomfortable truth: most token waste isn't a tooling problem. It's a configuration problem. You handed an agent a firehose and are surprised it's using it. Let's plug some holes first.

### The `AGENT.md` File: The Forgotten Budget Manager

Most people treat `AGENT.md` (or `CLAUDE.md`, `AGENTS.md`, depending on your flavour of agent) as a place to dump project context. That's only half right. It's also your first and best line of defence against runaway behaviour.

**Stop loops before they compound.** Hard iteration caps are the single biggest lever most people aren't pulling. If your agent hasn't resolved something after N attempts, it should halt — not heroically try a 7th variation of the same broken `npm install` command. Add explicit instructions like:

```
- Cap each debug loop at 2-3 attempts, then stop and report the blocker.
- Do NOT retry the same approach more than once. If something fails, form a new hypothesis.
- If an assumption cannot be verified with available tools, STOP and ask.
```

This is unglamorous. It will not get a GitHub star. But it will save you more money than any compression library.

**Budget guardrails at the agent level.** This is the part people consistently skip. Setting per-agent spend limits means a runaway loop hits a ceiling and dies quietly rather than you discovering the damage on your invoice at 9am on a Monday. Tools like [Airia](https://airia.com/) have this built in if you want a purpose-built solution, but even a simple token counter with a hard stop in your orchestration layer goes a long way.

**Preprocess your error logs. Seriously.** Dumping a 4,000-line stack trace into context and hoping the agent figures it out is like handing someone a bag of shredded documents and asking them to read the memo. Strip it first. Pass only:

- The error type
- The failing command
- The last relevant stack frame

That's it. Not the whole dump. Not every timestamp. Not six repetitions of the same exception. Just the signal. The difference in token spend per call can be significant — and your agent will actually perform *better* because there's less noise to wade through.

### Skills: Teach Once, Reference Forever

Instead of re-explaining project conventions every single conversation, encode them as reusable "skills" or instructions that the agent can load selectively. Think of it as teaching your agent a trade rather than micromanaging every task. Many agent frameworks support this natively — and it means you stop paying to re-explain your folder structure on every invocation.

---

## Part 2: Tools That Actually Help (With Receipts)

Okay, you've done the boring configuration stuff. Good. Now let's talk about tools. These fall into four rough categories: compressing what goes *in*, compressing what comes *out*, being smarter about *what* goes in, and full agent harnesses that handle all of the above.

### Input Compression: Put Your Context on a Diet

**[Headroom](https://github.com/headroomlabs-ai/headroom)**

Headroom is a context compression library that trims your input tokens before they even reach the model. The core idea is smart truncation and summarisation — keeping the semantically important parts of your context window without feeding the model a novel-length history. If you're building agents that accumulate long conversation histories or tool outputs, this is worth a look. Less in = less cost = faster responses = everyone wins.

### Code Search: Stop Pasting Your Entire Codebase

One of the most common token crimes I see is people dumping entire files — or worse, entire repositories — into context because they're not sure what's relevant. The fix isn't a bigger context window. The fix is smarter retrieval.

**Graphify** builds a semantic graph of your codebase, so instead of "here's all 80 files, good luck," you get "here are the 4 files that are actually relevant to this function call." Token spend on code tasks can drop dramatically when your retrieval is surgical rather than blunt.

**Semble** takes a similar approach — semantic code search that lets the agent pull only what it needs, when it needs it. Rather than pre-loading context, you pull it lazily. Your context window stays lean, your costs stay sane.

The pattern here is the same as good database design: don't `SELECT *` when you only need three columns.

### Output Compression: When Your Agent is Too Verbose for Its Own Good

Agents are, as a species, verbose. Ask one to rename a variable and it will explain its reasoning in three paragraphs, write a changelog entry, and propose a refactor of the surrounding module. We love the enthusiasm. We do not love the bill.

**[Caveman](https://github.com/JuliusBrussee/caveman)**

Caveman is a Claude Code plugin that forces the model into a compressed output mode — essentially stripping responses down to the functional minimum. The results are... mixed, and I appreciate that the data here is honest.

For simple Q&A and small tasks? The savings are modest at best, and sometimes Caveman actually *costs more* — likely because the compression overhead and longer wall times eat into any gains:

| Task | Mode | Cost | Wall Time |
|---|---|---|---|
| Code review | Regular | $0.43 | 20m 27s |
| Code review | Caveman | $0.46 | 41m 46s |
| Code review | Caveman Ultra | $0.44 | 3m 18s |

But for larger summarisation tasks — things like "summarise these files and list the TODOs" — Caveman Ultra shines:

| Task | Mode | Cost | Wall Time |
|---|---|---|---|
| File summary | Regular | $0.26 | 1m 20s |
| File summary | Caveman Ultra | $0.09 | 39s |

That's a **~64% cost reduction** and the task completed in less than half the time. The lesson: Caveman isn't a silver bullet you fire at everything. It's a scalpel for the right kind of work — large-context summarisation where the model's verbosity is the problem. Point it at a code review and you might just make things worse. Point it at a documentation dump and it sings.

> Reported savings elsewhere have been as high as 75% in specific setups ([source](https://www.qwe.edu.pl/tutorial/caveman-claude-reduce-tokens-75-percent/)), and The New Stack covered the approach in more depth if you want to go deeper ([source](https://thenewstack.io/caveman-mode-token-savings/)).

**[Ponytail](https://medium.com/coding-nexus/ponytail-the-ai-plugin-that-makes-claude-code-write-54-less-code-without-breaking-anything-df29842c8ff6)**

Ponytail is another Claude Code plugin with a different philosophy: rather than compressing the output format, it teaches the agent to write *less code* in the first place — targeting a claimed 54% reduction in generated code without breaking functionality. The idea is to aggressively discourage the model's habit of over-engineering and over-explaining. Instead of generating a helper utility, an abstraction layer, *and* a README, it just... does the thing. Novel concept.

---

### Complete Agent Harnesses: If You Want Someone Else to Solve This

If you'd rather not assemble these pieces yourself — input compression here, loop guards there, output trimming somewhere else — there are complete harnesses being built to handle all of it.

**[Pi](https://pi.dev/)**

Pi is a full agent orchestration layer that handles a lot of the efficiency concerns natively. [Benchmarks against vanilla Claude setups](https://warden.sentry.dev/benchmarking) show meaningful cost improvements, and it packages things like budget controls, smarter context management, and loop prevention into a single product. It won't appeal to the "I want to understand exactly what's happening" crowd, but if you want to stop thinking about this and get back to actually building things, it's worth evaluating.

---

## Part 3: The Meta-Lesson Nobody Wants to Hear

You've read this far, so I'll reward you with the uncomfortable synthesis.

The tools are real. Some of them work very well in the right context. But the biggest single lever — by a significant margin — is stopping bad loops early.

Think about it from a first principles perspective. A single runaway debugging loop that spins 15 iterations on a broken assumption doesn't just waste 15x the tokens on that loop. It fills your context window with garbage, which makes subsequent reasoning worse, which causes *more* iterations, which fills the window further. It's a compounding disaster, and no compression library in the world can rescue you from it after the fact.

What actually works, in rough order of impact:

1. **Hard iteration caps** — If the agent hasn't solved it in 2-3 attempts, force a new hypothesis or escalate to human review. This alone is the biggest single bleed you can stop.
2. **Structured error preprocessing** — Summarise logs into structured facts *before* they hit the context window. Pass error type + immediate context only.
3. **Surgical retrieval** — Use code search tools (Graphify, Semble) instead of dumping files wholesale.
4. **Output compression on the right tasks** — Caveman Ultra for summarisation-heavy work. Ponytail if verbosity is your main complaint.
5. **Full harnesses** — Pi and similar if you want it all packaged up.

The model isn't the problem. The cheapest model in the world will still burn through your budget if it's spinning in a loop, reading your entire codebase on every call, and writing four paragraphs to tell you it renamed a variable.

---

## Conclusion: Your Token Budget is a Resource, Not a Tax

Tokens aren't infinite. Neither is your patience, or your cloud budget line. The good news is that most of the waste is preventable — and the fixes range from free (configuration) to very cheap (most of these tools).

The bad news is that none of this is as satisfying as installing a library and watching a metric go down. The biggest wins require discipline: structured instructions, loop guards, preprocessed inputs, surgical context. It's the AI equivalent of eating vegetables. It's not glamorous, but your future self — the one looking at next month's invoice — will be grateful.

Now go put a loop cap in your `AGENT.md`. I'll wait.

---

*Sources and further reading:*
- *[Caveman benchmarks and tutorial](https://www.qwe.edu.pl/tutorial/caveman-claude-reduce-tokens-75-percent/)*
- *[Caveman Mode — The New Stack](https://thenewstack.io/caveman-mode-token-savings/)*
- *[Pi vs Claude harness benchmarks](https://warden.sentry.dev/benchmarking)*
- *[Ponytail — Coding Nexus](https://medium.com/coding-nexus/ponytail-the-ai-plugin-that-makes-claude-code-write-54-less-code-without-breaking-anything-df29842c8ff6)*
- *[Cutting LLM token costs with RTK — CodePointer](https://codepointer.substack.com/p/cutting-llm-token-costs-with-rtk)*

---

Single Pass Sonnet 4.6
# Stop Burning Money: Token-Saving Practices (and the Tools That Actually Help)

---

## The Context Window is Not a Landfill

You're anxiously watching the progress bar on your monthly AI budget allocation as your favorite little buddy tries the same command line action for the 5th time. _This time he's gonna get it right_, you think to yourself.

A little while later you're scratching your head as the agent you tasked with implementing a simple new endpoint generates a two-page design document describing the 15 steps needed. You let out a sigh and start implementing yourself.

If you've been using AI coding agents in the past six months, this should sound familiar. And you've either accepted this as the price of the future, or — like me — have been desperately trying to stretch that precious token budget before your VP of Engineering notices the AWS bill.

In this post, I'll share some hard-won insights, configuration tricks, and a handful of tools that'll make your coding buddy last a little longer — without making it dumber. Let's go.

---

## Part 1: Before You Install Anything — Fix Your Configuration

Here's the uncomfortable truth: most token waste isn't a tooling problem. It's a configuration problem. You handed an agent a firehose and are surprised it's using it. Let's plug some holes first.

### The `AGENT.md` File: The Forgotten Budget Manager

Most people treat `AGENT.md` (or `CLAUDE.md`, `AGENTS.md`, depending on your flavour of agent) as a place to dump project context. That's only half right. It's also your first and best line of defence against runaway behaviour.

**Stop loops before they compound.** Hard iteration caps are the single biggest lever most people aren't pulling. If your agent hasn't resolved something after N attempts, it should halt — not heroically try a 7th variation of the same broken `npm install` command. Add explicit instructions like:

Collapse

Run

Save Copy

9

1

2

3

›

- Cap each debug loop at 2-3 attempts, then stop and report the blocker.

- Do NOT retry the same approach more than once. If something fails, form a new hypothesis.

- If an assumption cannot be verified with available tools, STOP and ask.

This is unglamorous. It will not get a GitHub star. But it will save you more money than any compression library.

**Budget guardrails at the agent level.** This is the part people consistently skip. Setting per-agent spend limits means a runaway loop hits a ceiling and dies quietly rather than you discovering the damage on your invoice at 9am on a Monday. Tools like [Airia](https://airia.com/) have this built in if you want a purpose-built solution, but even a simple token counter with a hard stop in your orchestration layer goes a long way.

**Preprocess your error logs. Seriously.** Dumping a 4,000-line stack trace into context and hoping the agent figures it out is like handing someone a bag of shredded documents and asking them to read the memo. Strip it first. Pass only:

- The error type
- The failing command
- The last relevant stack frame

That's it. Not the whole dump. Not every timestamp. Not six repetitions of the same exception. Just the signal. The difference in token spend per call can be significant — and your agent will actually perform _better_ because there's less noise to wade through.

### Skills: Teach Once, Reference Forever

Instead of re-explaining project conventions every single conversation, encode them as reusable "skills" or instructions that the agent can load selectively. Think of it as teaching your agent a trade rather than micromanaging every task. Many agent frameworks support this natively — and it means you stop paying to re-explain your folder structure on every invocation.

---

## Part 2: Tools That Actually Help (With Receipts)

Okay, you've done the boring configuration stuff. Good. Now let's talk about tools. These fall into four rough categories: compressing what goes _in_, compressing what comes _out_, being smarter about _what_ goes in, and full agent harnesses that handle all of the above.

### Input Compression: Put Your Context on a Diet

**[Headroom](https://github.com/headroomlabs-ai/headroom)**

Headroom is a context compression library that trims your input tokens before they even reach the model. The core idea is smart truncation and summarisation — keeping the semantically important parts of your context window without feeding the model a novel-length history. If you're building agents that accumulate long conversation histories or tool outputs, this is worth a look. Less in = less cost = faster responses = everyone wins.

### Code Search: Stop Pasting Your Entire Codebase

One of the most common token crimes I see is people dumping entire files — or worse, entire repositories — into context because they're not sure what's relevant. The fix isn't a bigger context window. The fix is smarter retrieval.

**Graphify** builds a semantic graph of your codebase, so instead of "here's all 80 files, good luck," you get "here are the 4 files that are actually relevant to this function call." Token spend on code tasks can drop dramatically when your retrieval is surgical rather than blunt.

**Semble** takes a similar approach — semantic code search that lets the agent pull only what it needs, when it needs it. Rather than pre-loading context, you pull it lazily. Your context window stays lean, your costs stay sane.

The pattern here is the same as good database design: don't `SELECT *` when you only need three columns.

### Output Compression: When Your Agent is Too Verbose for Its Own Good

Agents are, as a species, verbose. Ask one to rename a variable and it will explain its reasoning in three paragraphs, write a changelog entry, and propose a refactor of the surrounding module. We love the enthusiasm. We do not love the bill.

**[Caveman](https://github.com/JuliusBrussee/caveman)**

Caveman is a Claude Code plugin that forces the model into a compressed output mode — essentially stripping responses down to the functional minimum. The results are... mixed, and I appreciate that the data here is honest.

For simple Q&A and small tasks? The savings are modest at best, and sometimes Caveman actually _costs more_ — likely because the compression overhead and longer wall times eat into any gains:

|Task|Mode|Cost|Wall Time|
|---|---|---|---|
|Code review|Regular|$0.43|20m 27s|
|Code review|Caveman|$0.46|41m 46s|
|Code review|Caveman Ultra|$0.44|3m 18s|

But for larger summarisation tasks — things like "summarise these files and list the TODOs" — Caveman Ultra shines:

|Task|Mode|Cost|Wall Time|
|---|---|---|---|
|File summary|Regular|$0.26|1m 20s|
|File summary|Caveman Ultra|$0.09|39s|

That's a **~64% cost reduction** and the task completed in less than half the time. The lesson: Caveman isn't a silver bullet you fire at everything. It's a scalpel for the right kind of work — large-context summarisation where the model's verbosity is the problem. Point it at a code review and you might just make things worse. Point it at a documentation dump and it sings.

> Reported savings elsewhere have been as high as 75% in specific setups ([source](https://www.qwe.edu.pl/tutorial/caveman-claude-reduce-tokens-75-percent/)), and The New Stack covered the approach in more depth if you want to go deeper ([source](https://thenewstack.io/caveman-mode-token-savings/)).

**[Ponytail](https://medium.com/coding-nexus/ponytail-the-ai-plugin-that-makes-claude-code-write-54-less-code-without-breaking-anything-df29842c8ff6)**

Ponytail is another Claude Code plugin with a different philosophy: rather than compressing the output format, it teaches the agent to write _less code_ in the first place — targeting a claimed 54% reduction in generated code without breaking functionality. The idea is to aggressively discourage the model's habit of over-engineering and over-explaining. Instead of generating a helper utility, an abstraction layer, _and_ a README, it just... does the thing. Novel concept.

---

### Complete Agent Harnesses: If You Want Someone Else to Solve This

If you'd rather not assemble these pieces yourself — input compression here, loop guards there, output trimming somewhere else — there are complete harnesses being built to handle all of it.

**[Pi](https://pi.dev/)**

Pi is a full agent orchestration layer that handles a lot of the efficiency concerns natively. [Benchmarks against vanilla Claude setups](https://warden.sentry.dev/benchmarking) show meaningful cost improvements, and it packages things like budget controls, smarter context management, and loop prevention into a single product. It won't appeal to the "I want to understand exactly what's happening" crowd, but if you want to stop thinking about this and get back to actually building things, it's worth evaluating.

---

## Part 3: The Meta-Lesson Nobody Wants to Hear

You've read this far, so I'll reward you with the uncomfortable synthesis.

The tools are real. Some of them work very well in the right context. But the biggest single lever — by a significant margin — is stopping bad loops early.

Think about it from a first principles perspective. A single runaway debugging loop that spins 15 iterations on a broken assumption doesn't just waste 15x the tokens on that loop. It fills your context window with garbage, which makes subsequent reasoning worse, which causes _more_ iterations, which fills the window further. It's a compounding disaster, and no compression library in the world can rescue you from it after the fact.

What actually works, in rough order of impact:

1. **Hard iteration caps** — If the agent hasn't solved it in 2-3 attempts, force a new hypothesis or escalate to human review. This alone is the biggest single bleed you can stop.
2. **Structured error preprocessing** — Summarise logs into structured facts _before_ they hit the context window. Pass error type + immediate context only.
3. **Surgical retrieval** — Use code search tools (Graphify, Semble) instead of dumping files wholesale.
4. **Output compression on the right tasks** — Caveman Ultra for summarisation-heavy work. Ponytail if verbosity is your main complaint.
5. **Full harnesses** — Pi and similar if you want it all packaged up.

The model isn't the problem. The cheapest model in the world will still burn through your budget if it's spinning in a loop, reading your entire codebase on every call, and writing four paragraphs to tell you it renamed a variable.

---

## Conclusion: Your Token Budget is a Resource, Not a Tax

Tokens aren't infinite. Neither is your patience, or your cloud budget line. The good news is that most of the waste is preventable — and the fixes range from free (configuration) to very cheap (most of these tools).

The bad news is that none of this is as satisfying as installing a library and watching a metric go down. The biggest wins require discipline: structured instructions, loop guards, preprocessed inputs, surgical context. It's the AI equivalent of eating vegetables. It's not glamorous, but your future self — the one looking at next month's invoice — will be grateful.

Now go put a loop cap in your `AGENT.md`. I'll wait.

---

_Sources and further reading:_

- _[Caveman benchmarks and tutorial](https://www.qwe.edu.pl/tutorial/caveman-claude-reduce-tokens-75-percent/)_
- _[Caveman Mode — The New Stack](https://thenewstack.io/caveman-mode-token-savings/)_
- _[Pi vs Claude harness benchmarks](https://warden.sentry.dev/benchmarking)_
- _[Ponytail — Coding Nexus](https://medium.com/coding-nexus/ponytail-the-ai-plugin-that-makes-claude-code-write-54-less-code-without-breaking-anything-df29842c8ff6)_
- _[Cutting LLM token costs with RTK — CodePointer](https://codepointer.substack.com/p/cutting-llm-token-costs-with-rtk)_

---

There you go! A few notes on what I did and some questions for you:

1. **Caveman data** — I presented the benchmark numbers honestly, including the cases where it didn't help. That felt more credible than overselling it. Happy to reframe if you want a more optimistic spin.
2. **Graphify and Semble** — I had limited detail on these from your research notes, so I described them based on the pattern (semantic code retrieval). If you have more specific details (benchmarks, how they work under the hood), I can make those sections much richer.
3. **Pi** — Same situation. I kept it short and pointed to the benchmark link. More detail = better section if you have it.
4. **Tone** — I tried to balance technical credibility with the quirky/adventurous voice. Want me to dial the humour up or down anywhere?
5. **Length** — This is moderately long. Want a shorter punchy version, or is this about the right depth?
