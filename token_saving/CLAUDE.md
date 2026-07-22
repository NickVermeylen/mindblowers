# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a research and writing workspace for an "Insights" blog post on token-saving strategies for AI coding agents. There is no build system or test suite — the deliverable is written content.

## File Structure

- `Insight - How to cut costs and stretch budgets.md` — the primary working file. Contains:
  - An outline/research notes section at the top
  - Benchmarking data (Caveman vs. regular mode, across task types)
  - A complete draft of the finished article (written in a single pass by Sonnet 4.6)
  - A second near-identical pass of the same article further down — these are drafts, not distinct sections
- `Insight - Token savings.docx` — likely an alternate format of the same article

## Article Content Summary

The article covers token-saving strategies in three areas:
1. **Configuration** (`AGENT.md`/`CLAUDE.md` loop caps, error log preprocessing, skills)
2. **Tools** — input compression (Headroom), code search (Graphify, Semble), output compression (Caveman, Ponytail), and full harnesses (Pi)
3. **Meta-lesson** — loop prevention is the highest-leverage fix; tooling is secondary

### Key benchmark data (from the notes section)
| Task | Mode | Cost | Wall Time |
|---|---|---|---|
| Code review | Regular | $0.43 | 20m 27s |
| Code review | Caveman Ultra | $0.44 | 3m 18s |
| File summary | Regular | $0.26 | 1m 20s |
| File summary | Caveman Ultra | $0.09 | 39s |

Caveman Ultra saves ~64% on summarisation tasks but adds cost on simple code review.

## Working With This Content

- The markdown file contains two near-duplicate draft passes — when editing, treat the first complete draft (lines ~114–265) as the canonical version unless told otherwise.
- Benchmark numbers from the notes section (lines 52–97) are the source of truth; the article prose is derived from them.
- Sections on Graphify, Semble, and Pi are intentionally thin — the author lacked benchmark data for them at time of writing.
