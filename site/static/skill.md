# LLM Weather Report — Agent Skill

You are reading results from the LLM Weather Report, a tool that tracks reasoning capability drift across LLM models over time.

## What This Data Is

A fixed set of 7 reasoning prompts is run across multiple LLM models on a schedule (6x daily). Each model's response is evaluated individually for **correctness** (boolean) and **reasoning quality** (1-5 score) by a panel of 3 judge models using majority vote.

## How To Read The Scorecard

The scorecard is a model × prompt grid:

- `✓ (4.67)` — model answered correctly, average quality score 4.67/5
- `✗ (1.67)` — model answered incorrectly, average quality score 1.67/5
- `—` — model was unavailable or errored

**Prompt categories:** logic, math, spatial reasoning, causality, code comprehension, ambiguity resolution, common sense.

## How To Read Drift Alerts

Drift alerts flag changes between consecutive runs:

- **REGRESSION** — model was correct, now incorrect. This is the most important signal.
- **IMPROVEMENT** — model was incorrect, now correct.
- **SCORE_DROP** — model still correct but quality score dropped by ≥1.0 point.
- **SCORE_RISE** — model still correct and quality score rose by ≥1.0 point.

## How To Read Model Status

Each model is assigned a status based on drift:

- **stable** (→) — no drift detected since last run
- **up** (↑) — model improved (correctness or score rise)
- **down** (↓) — model regressed (correctness loss or score drop). Down overrides up.

## How To Access Data

- **Latest report (HTML):** `/` — the home page shows the most recent scorecard
- **Individual run (HTML):** `/runs/<run-id>/` — full scorecard for a specific run
- **Individual run (Markdown):** `/runs/<run-id>/report.md` — machine-readable markdown
- **Individual run (JSON):** `/runs/<run-id>/data.json` — raw structured data with scorecard, drift, status, and previous run comparison
- **All runs index:** `/llms.txt` — plain text index of all runs with headlines and links to markdown/JSON
- **Raw data:** Available in the git repo under `runs/<run-id>/responses.json` and `runs/<run-id>/judgments.json`

## Models Tracked

The current contestant models are listed in the scorecard. Models without API keys configured are automatically skipped (e.g., Ollama when running in CI).

## Interpreting Results

- **All ✓ with high scores (4.5+):** Model is performing well on reasoning tasks. This is the baseline.
- **A ✗ appearing:** The model got a reasoning question wrong. Check which prompt category failed — this indicates a specific capability gap.
- **Score dropping while still ✓:** The model still gets the right answer but its reasoning quality is degrading. Early warning sign.
- **REGRESSION alert:** A model that previously answered correctly now fails. This is the strongest drift signal — something changed in the model's reasoning capability.

## For Programmatic Access

Fetch `/llms.txt` for a structured index of all runs. Each run links to its markdown and JSON versions.

- **Markdown:** `/runs/<run-id>/report.md` — human-readable, parseable table format
- **JSON:** `/runs/<run-id>/data.json` — structured data with fields: `run_id`, `date`, `headline`, `status`, `scorecard`, `drift`, `previous`

The JSON endpoint is the recommended way to consume data programmatically. The `previous` field contains the prior run's scorecard for comparison.
