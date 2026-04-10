# LLM Weather Report

Track reasoning capability drift across LLM models. Runs the same curated prompts against multiple models, blindly judges the results with majority vote, and publishes a static site showing who's on top.

## How it works

1. **Run** — sends 7 reasoning prompts (logic, math, spatial, code, etc.) to all configured models via [LiteLLM](https://github.com/BerriAI/litellm)
2. **Judge** — shuffles responses anonymously, sends to 3 judge models, majority vote picks winners
3. **Report** — generates a leaderboard with drift detection (who moved up/down since last run)
4. **Publish** — builds a Hugo static site with the results

## Setup

```bash
uv sync
```

Set API keys for the providers you want to test:

```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export GEMINI_API_KEY=...
export GROQ_API_KEY=gsk_...
```

Models without keys are skipped automatically.

## Usage

```bash
# Run the full pipeline
uv run llm-weather run

# Regenerate reports from existing data
uv run llm-weather report runs/2026-04-10T14-00-00/

# Rebuild all Hugo content
uv run llm-weather publish
```

## Configuration

**prompts.yaml** — reasoning prompts to test. Small curated set across categories.

**models.yaml** — which models compete and which models judge:

```yaml
contestants:
  - model: openai/gpt-4.1
  - model: anthropic/claude-sonnet-4-6
  - model: google/gemini-2.5-pro
  - model: ollama/llama3
  # ...

judges:
  - model: openai/gpt-4.1
  - model: anthropic/claude-sonnet-4-6
  - model: google/gemini-2.5-pro
```

## Scheduling

Runs 6x daily via GitHub Actions (`.github/workflows/weather.yml`). Results commit back to the repo, Cloudflare Pages auto-deploys.

## Output

Each run creates `runs/<timestamp>/` with:
- `responses.json` — raw model responses with latency and token counts
- `judgments.json` — blind judge verdicts and shuffle mappings
- `summary.md` — leaderboard and drift
- `detail.md` — per-prompt breakdowns with judge reasoning
