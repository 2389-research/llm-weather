---
title: About & Methodology
---

The LLM Weather Report tracks reasoning capability drift across large language models. Instead of benchmarking models against each other, it monitors whether individual models maintain consistent performance on a fixed set of reasoning tasks over time.

## Why

Model providers update their models constantly — weight updates, system prompt changes, infrastructure migrations. These changes can silently alter reasoning behavior. A model that correctly solved a logic puzzle yesterday might fail today. The LLM Weather Report catches these changes.

## How It Works

### Prompts

A fixed set of 7 reasoning prompts covers:

- **Logic** — syllogistic and deductive reasoning
- **Math** — arithmetic and word problems
- **Spatial reasoning** — directional and relational questions
- **Causality** — cause-and-effect chain reasoning
- **Code comprehension** — reading and tracing code
- **Ambiguity resolution** — handling vague or underspecified questions
- **Common sense** — everyday physical and social reasoning

Prompts are deliberately simple. The goal is not to find the hardest problems but to establish a stable baseline that should always be answered correctly. When a model fails one of these, something changed.

### Multi-Sample Evaluation

Each prompt is sent to each model multiple times (default: 2 samples per prompt per model). This distinguishes real drift from stochastic noise — if a model gets it right once and wrong once, that's different from getting it wrong twice.

### Judging

Each response is evaluated independently by a panel of 3 judge models for:

- **Correctness** (boolean) — is the answer right?
- **Reasoning quality** (1–5 score) — how good is the reasoning?

Correctness is determined by majority vote across all judges × samples. Scores are averaged. This cross-model judging reduces bias from any single evaluator.

### Drift Detection

Each run is compared against the previous run. Four types of drift are flagged:

| Type | Meaning | Severity |
|------|---------|----------|
| **REGRESSION** | Was correct, now incorrect | High — capability loss |
| **IMPROVEMENT** | Was incorrect, now correct | Positive signal |
| **SCORE_DROP** | Still correct, score fell ≥1.0 | Warning — reasoning degrading |
| **SCORE_RISE** | Still correct, score rose ≥1.0 | Positive signal |

### Model Status

Each model gets a per-run status:

- **→ stable** — no drift detected
- **↑ up** — improving (correctness gained or score rising)
- **↓ down** — regressing (correctness lost or score dropping). Down overrides up — if a model both improved and regressed in the same run, it's marked down.

### Schedule

Runs execute 6 times daily via GitHub Actions. Results are committed to the repository and deployed automatically.

## Models Tracked

The current contestant and judge models are configured in `models.yaml` in the project repository. Models without API keys configured are automatically skipped.

## Data Access

All data is available in multiple formats:

- **HTML** — human-readable pages at each run URL
- **Markdown** — `/runs/<id>/report.md` for each run
- **JSON** — `/runs/<id>/data.json` with full scorecard, drift, status, and previous run data
- **llms.txt** — `/llms.txt` plain text index of all runs
- **Agent skill** — `/skill.md` instructions for AI agents consuming this data
- **Source** — full run data in the [GitHub repository](https://github.com/2389-research/llm-weather)

## Built With

- [LiteLLM](https://github.com/BerriAI/litellm) — unified API for all model providers
- [Hugo](https://gohugo.io) — static site generation
- [GitHub Actions](https://github.com/features/actions) — scheduled execution
- [Netlify](https://www.netlify.com) — hosting and deployment

## About

A [2389 Research](https://2389.ai) project. Source code on [GitHub](https://github.com/2389-research/llm-weather).
