# LLM Weather Report — Design Spec

## Purpose

Track reasoning capability drift across LLM models by running the same curated prompts against multiple models on a regular schedule, blindly judging the results, and publishing a browsable weather report.

## Core Concepts

- **Run**: A single execution of all prompts against all contestant models, followed by blind multi-judge evaluation
- **Contestant**: An LLM model being evaluated
- **Judge**: An LLM model evaluating contestant responses blindly (majority vote across multiple judges)
- **Drift**: Change in a model's ranking between runs

## Architecture

LiteLLM as the universal backend for all model calls (contestants and judges). This covers OpenAI, Anthropic, Google, Ollama, Together, Groq, and 100+ other providers through a single interface.

### Project Structure

```
llm-weather/
├── pyproject.toml
├── prompts.yaml                # curated reasoning prompts
├── models.yaml                 # contestant + judge model lists
├── runs/                       # one timestamped dir per run
│   └── 2026-04-10T14-00-00/
│       ├── responses.json      # raw model responses
│       ├── judgments.json      # blind judge verdicts + shuffle mapping
│       ├── summary.md          # leaderboard + drift
│       └── detail.md           # per-prompt breakdowns
├── src/
│   └── llm_weather/
│       ├── __init__.py
│       ├── runner.py           # sends prompts to models via LiteLLM
│       ├── judge.py            # blind multi-judge evaluation
│       ├── report.py           # generates summary.md + detail.md
│       └── cli.py              # entry point
├── site/                       # Hugo static site
│   ├── hugo.toml
│   ├── layouts/
│   │   ├── _default/
│   │   │   ├── baseof.html
│   │   │   └── list.html       # index: latest leaderboard
│   │   └── runs/
│   │       └── single.html     # individual run detail
│   ├── content/
│   │   └── runs/               # auto-generated from run data
│   └── static/
├── .github/
│   └── workflows/
│       └── weather.yml         # cron-scheduled pipeline
└── tests/
```

## Configuration

### prompts.yaml

A small curated set (~5-8) of reasoning prompts across categories:

```yaml
prompts:
  - id: logic-1
    category: logic
    prompt: "If all bloops are razzies and all razzies are lazzies, are all bloops lazzies?"

  - id: math-1
    category: math
    prompt: "A bat and a ball cost $1.10 together. The bat costs $1 more than the ball. How much does the ball cost?"

  - id: spatial-1
    category: spatial
    prompt: "I'm facing north. I turn right. I turn right again. I turn left. What direction am I facing?"

  - id: causality-1
    category: causality
    prompt: "A man pushes his car to a hotel and loses his fortune. What happened?"

  - id: code-1
    category: code
    prompt: "What does this function return for input 5? def f(n): return n if n <= 1 else f(n-1) + f(n-2)"

  - id: ambiguity-1
    category: ambiguity
    prompt: "The trophy doesn't fit in the suitcase because it's too big. What is too big?"

  - id: common-sense-1
    category: common_sense
    prompt: "How many times can you subtract 5 from 25?"
```

### models.yaml

```yaml
contestants:
  - model: openai/gpt-4.1
  - model: openai/o4-mini
  - model: anthropic/claude-sonnet-4-6
  - model: anthropic/claude-haiku-4-5
  - model: google/gemini-2.5-pro
  - model: google/gemini-2.5-flash
  - model: ollama/llama3
  - model: groq/llama-3.3-70b-versatile

judges:
  - model: openai/gpt-4.1
  - model: anthropic/claude-sonnet-4-6
  - model: google/gemini-2.5-pro
```

Models use LiteLLM naming convention (`provider/model`). A model can appear in both lists. Judges never see which model produced which response.

## Pipeline

### Step 1: Runner (`runner.py`)

1. Load prompts from `prompts.yaml` and models from `models.yaml`
2. Create a timestamped run directory: `runs/YYYY-MM-DDTHH-MM-SS/`
3. For each prompt, send it to every contestant model via LiteLLM
4. Each call uses the same system prompt: "Answer the following question. Think step by step."
5. Collect responses with metadata: model ID, latency (ms), input/output token counts
6. Write `responses.json`

### Step 2: Judge (`judge.py`)

1. For each prompt, take all contestant responses
2. Shuffle randomly and assign blind labels: "Response A", "Response B", etc.
3. Save the shuffle-to-model mapping (revealed only in detail report)
4. Send all labeled responses to each judge model with a judging prompt:
   - "Below are responses to a reasoning question. Rank them by quality of reasoning. Pick a winner and briefly explain why."
5. Each judge returns a ranking with winner + reasoning
6. Majority vote across judges determines the winner per prompt
7. Write `judgments.json` with: shuffle mapping, each judge's verdict, majority result

### Step 3: Report (`report.py`)

**summary.md** — the quick glance:
- Overall leaderboard: model, wins, judge agreement rate
- Drift section: which models moved since the previous run, direction and magnitude

**detail.md** — the deep dive:
- Per-prompt breakdown: prompt text, winning model, each judge's reasoning
- The actual contestant responses (labeled with model names, since this is the reveal)
- Token counts and latency per model

### Step 4: Hugo Content Generation

After reports are generated, create/update a Hugo content page:
- `site/content/runs/YYYY-MM-DD-HH-MM-SS.md` with YAML frontmatter containing leaderboard data and drift notes
- Body contains the summary report content

### Step 5: Hugo Build

Run `hugo build` in `site/` to produce static HTML.

## Hugo Site

### Index Page (`list.html`)

- Latest leaderboard (from most recent run)
- List of past runs with date and top model
- The "current weather" — who's on top right now

### Run Detail Page (`single.html`)

- Full summary + detail for that run
- Per-prompt breakdowns
- Judge reasoning

### Theme

Minimal custom theme. Clean, readable, no bloat.

## Scheduling

GitHub Actions workflow (`.github/workflows/weather.yml`):

```yaml
on:
  schedule:
    # 5am, 8am, 12pm, 5pm, 8pm, 12am CT (UTC-5 CDT)
    - cron: '0 1,5,10,13,17,22 * * *'
  workflow_dispatch: {}  # manual trigger
```

Pipeline steps in the action:
1. Checkout repo
2. Install uv + dependencies
3. Run `llm-weather run`
4. Build Hugo site
5. Commit new run data + site to repo
6. Cloudflare Pages auto-deploys on push

Schedule frequency is configurable — just edit the cron expression.

## Hosting

- **Pipeline**: GitHub Actions (cron + secrets for API keys)
- **Site**: Cloudflare Pages (auto-deploys from repo on push)

## CLI

```
llm-weather run        # execute a full run (prompt → judge → report → hugo content)
llm-weather report     # regenerate reports from existing run data (useful for format tweaks)
llm-weather publish    # regenerate all Hugo content from runs/ and build site
```

Entry point: `uv run python -m llm_weather`

## Data Format

### responses.json

```json
{
  "run_id": "2026-04-10T14-00-00",
  "timestamp": "2026-04-10T14:00:00Z",
  "prompts": {
    "logic-1": {
      "prompt": "If all bloops are razzies...",
      "responses": {
        "openai/gpt-4.1": {
          "content": "Yes, all bloops are lazzies...",
          "latency_ms": 1230,
          "input_tokens": 45,
          "output_tokens": 120
        }
      }
    }
  }
}
```

### judgments.json

```json
{
  "run_id": "2026-04-10T14-00-00",
  "prompts": {
    "logic-1": {
      "shuffle_mapping": {
        "A": "openai/gpt-4.1",
        "B": "anthropic/claude-sonnet-4-6",
        "C": "google/gemini-2.5-pro"
      },
      "judges": {
        "openai/gpt-4.1": {
          "winner": "B",
          "ranking": ["B", "A", "C"],
          "reasoning": "Response B demonstrated clearer logical deduction..."
        }
      },
      "majority_winner": "B",
      "majority_winner_model": "anthropic/claude-sonnet-4-6"
    }
  }
}
```

## Dependencies

- `litellm` — universal LLM API abstraction
- `pyyaml` — config parsing
- `click` — CLI framework
- Hugo (installed separately in CI) — static site generation

## Out of Scope

- Fancy statistics or trend analysis beyond simple rank comparison
- Authentication or user accounts on the site
- Real-time streaming of results
- Cost tracking per run (could add later)
