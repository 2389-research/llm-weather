---
title: About & Methodology
---

The LLM Weather Report tracks whether large language models stay consistent over time. Not which one is smartest. Whether each one keeps doing what it did last week.

## What this tests

We test the raw LLM endpoint, not an agent. Each prompt is a single API call to the model's chat completions endpoint. No tool use, no multi-turn conversation, no retrieval, no agent scaffolding. The only system prompt is: *"Answer the following question. Think step by step."*

This matters. If a model starts failing the bat-and-ball problem, we want to know that the model changed, not that some wrapper broke. Agent frameworks, RAG pipelines, and tool use all add noise. We strip that away so when a score moves, the signal is clean.

## Why

Model providers update their models constantly. Weight tweaks, system prompt changes, infrastructure moves, quantization experiments. These changes rarely get announced, and they can break things. A model that nailed a logic puzzle on Tuesday might fumble it on Thursday, and nobody tells you.

We wanted to know when that happens, so we built this.

## How it works

### Prompts

Seven reasoning prompts, one per category:

- **Logic** — syllogistic and deductive reasoning
- **Math** — arithmetic and word problems
- **Spatial reasoning** — directional and relational questions
- **Causality** — cause-and-effect chain reasoning
- **Code comprehension** — reading and tracing code
- **Ambiguity resolution** — handling vague or underspecified questions
- **Common sense** — everyday physical and social reasoning

The prompts are deliberately easy. We're not trying to find the hardest problems. We're trying to establish a floor that should never break. When it does, something changed.

### Multi-sample evaluation

Each prompt goes to each model twice (configurable). This helps separate real drift from randomness. Getting it right once and wrong once is different from getting it wrong both times.

### Judging

Three judge models independently evaluate each response for:

- **Correctness** (boolean) — is the answer right?
- **Reasoning quality** (1-5 score) — how good is the reasoning?

Correctness uses majority vote across all judges and samples. Scores are averaged. Using multiple judge models reduces the chance that one evaluator's quirks skew results.

### Drift detection

Each run compares against the previous run. Four types of drift:

| Type | What happened | Severity |
|------|---------|----------|
| REGRESSION | Was correct, now incorrect | High |
| IMPROVEMENT | Was incorrect, now correct | Good news |
| SCORE_DROP | Still correct, but score fell ≥1.0 | Warning |
| SCORE_RISE | Still correct, score rose ≥1.0 | Good news |

### Model status

Each model gets a status per run:

- **→ stable** — nothing changed
- **↑ up** — got better (correctness gained or score rising)
- **↓ down** — got worse (correctness lost or score dropping). If a model both improved and regressed in the same run, we call it down. Regressions matter more.

### Schedule

Runs happen 6 times daily via GitHub Actions. Results get committed to the repo and deployed automatically.

## What we can't do

Seven prompts can't cover everything a model does. A model could regress on tasks we don't test, and we'd miss it. The prompts were chosen for stability and breadth, not coverage.

The judges are also LLMs. If the judge models drift at the same time or share the same blind spots, the evaluations could be wrong in ways that correlate. Majority voting helps, but it's not bulletproof.

Models are non-deterministic. A single failed sample might just be sampling noise. We flag it and watch for patterns rather than treating one failure as proof of drift.

The prompts are easy on purpose, which means we catch big regressions (a model that used to handle basic logic now can't) but we might miss subtler degradations in harder reasoning.

And we can only see what the API returns. We can't tell you whether a change was a weight update, a system prompt edit, a routing change, or a hardware swap. We report that something changed, not why.

## How this differs from benchmarks

MMLU, HumanEval, HELM, BIG-Bench, MT-Bench: these measure how well a model performs on a standardized test at a point in time. They're designed for comparing models and they typically run once per release.

We measure something different. We run the same prompts against the same deployed endpoints on a schedule, looking for changes between runs. A model could ace MMLU and still silently degrade on basic syllogisms between Tuesday and Thursday. No benchmark would catch that, because benchmarks don't re-test deployed endpoints every four hours.

We're also much simpler. HELM evaluates thousands of prompts across dozens of categories. We evaluate seven. That's the point. A small fixed prompt set makes drift detection unambiguous. When a score moves, you know exactly what changed.

## Models tracked

The current contestant and judge models are configured in `models.yaml` in the project repository. Models without API keys configured are automatically skipped.

## Data access

All data is available in multiple formats:

- **HTML** — human-readable pages at each run URL
- **Markdown** — `/runs/<id>/report.md` for each run
- **JSON** — `/runs/<id>/data.json` with full scorecard, drift, status, and previous run data
- **llms.txt** — `/llms.txt` plain text index of all runs
- **Agent skill** — `/skill.md` instructions for AI agents consuming this data
- **Source** — full run data in the [GitHub repository](https://github.com/2389-research/llm-weather)

## Source code

Everything is open source at [github.com/2389-research/llm-weather](https://github.com/2389-research/llm-weather). Key files:

- [prompts.yaml](https://github.com/2389-research/llm-weather/blob/main/prompts.yaml) — the 7 reasoning prompts
- [models.yaml](https://github.com/2389-research/llm-weather/blob/main/models.yaml) — contestant and judge model configuration
- [runner.py](https://github.com/2389-research/llm-weather/blob/main/src/llm_weather/runner.py) — sends prompts to models via LiteLLM
- [judge.py](https://github.com/2389-research/llm-weather/blob/main/src/llm_weather/judge.py) — evaluates each response for correctness and quality
- [report.py](https://github.com/2389-research/llm-weather/blob/main/src/llm_weather/report.py) — builds scorecard, detects drift, generates headlines
- [weather.yml](https://github.com/2389-research/llm-weather/blob/main/.github/workflows/weather.yml) — GitHub Actions workflow (cron schedule)
- [runs/](https://github.com/2389-research/llm-weather/tree/main/runs) — raw JSON data for every run

## Built with

- [LiteLLM](https://github.com/BerriAI/litellm) — unified API for all model providers
- [Hugo](https://gohugo.io) — static site generation
- [GitHub Actions](https://github.com/features/actions) — scheduled execution
- [Netlify](https://www.netlify.com) — hosting and deployment

## About

Built by [Harper Reed](https://harper.blog) at [2389 Research](https://2389.ai). Open source, open data.
