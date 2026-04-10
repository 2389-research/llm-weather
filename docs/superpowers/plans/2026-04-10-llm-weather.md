# LLM Weather Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a tool that runs curated reasoning prompts across multiple LLM models, blindly judges the results, tracks capability drift, and publishes a Hugo static site with the findings.

**Architecture:** Python CLI using LiteLLM as the universal model backend. YAML configs for prompts and models. JSON flat files per run for results. Hugo static site deployed via Cloudflare Pages, pipeline scheduled via GitHub Actions.

**Tech Stack:** Python 3.12, uv, LiteLLM, PyYAML, Click, Hugo, GitHub Actions

---

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `src/llm_weather/__init__.py`
- Create: `prompts.yaml`
- Create: `models.yaml`
- Create: `.gitignore`

- [ ] **Step 1: Initialize project with uv**

```bash
cd /Users/harper/Public/src/2389/llm-weather
uv init --lib --name llm-weather
```

This creates `pyproject.toml` and `src/llm_weather/__init__.py`.

- [ ] **Step 2: Add dependencies**

```bash
uv add litellm pyyaml click
uv add --dev pytest
```

- [ ] **Step 3: Update pyproject.toml entry point**

Add to `pyproject.toml`:

```toml
[project.scripts]
llm-weather = "llm_weather.cli:main"
```

- [ ] **Step 4: Create prompts.yaml**

Create `prompts.yaml` in project root:

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

- [ ] **Step 5: Create models.yaml**

Create `models.yaml` in project root:

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

- [ ] **Step 6: Create .gitignore**

```
.venv/
__pycache__/
*.pyc
runs/
site/public/
.env
```

- [ ] **Step 7: Commit scaffolding**

```bash
git add pyproject.toml uv.lock src/llm_weather/__init__.py prompts.yaml models.yaml .gitignore .python-version
git commit -m "feat: scaffold llm-weather project with dependencies and config"
```

---

### Task 2: Config Module

**Files:**
- Create: `src/llm_weather/config.py`
- Create: `tests/test_config.py`
- Create: `tests/fixtures/prompts.yaml`
- Create: `tests/fixtures/models.yaml`

- [ ] **Step 1: Create test fixtures**

Create `tests/fixtures/prompts.yaml`:

```yaml
prompts:
  - id: test-logic
    category: logic
    prompt: "Is A greater than B if A is 5 and B is 3?"

  - id: test-math
    category: math
    prompt: "What is 2 + 2?"
```

Create `tests/fixtures/models.yaml`:

```yaml
contestants:
  - model: openai/gpt-4.1
  - model: anthropic/claude-sonnet-4-6

judges:
  - model: openai/gpt-4.1
```

- [ ] **Step 2: Write failing tests for config loading**

Create `tests/test_config.py`:

```python
# ABOUTME: Tests for YAML config loading and validation.
# ABOUTME: Uses real fixture files, no mocking.

from pathlib import Path

from llm_weather.config import Prompt, ModelsConfig, load_prompts, load_models

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_prompts_returns_list_of_prompts():
    prompts = load_prompts(FIXTURES / "prompts.yaml")
    assert len(prompts) == 2
    assert all(isinstance(p, Prompt) for p in prompts)


def test_load_prompts_fields():
    prompts = load_prompts(FIXTURES / "prompts.yaml")
    first = prompts[0]
    assert first.id == "test-logic"
    assert first.category == "logic"
    assert "greater than" in first.prompt


def test_load_models_returns_config():
    config = load_models(FIXTURES / "models.yaml")
    assert isinstance(config, ModelsConfig)


def test_load_models_contestants():
    config = load_models(FIXTURES / "models.yaml")
    assert config.contestants == ["openai/gpt-4.1", "anthropic/claude-sonnet-4-6"]


def test_load_models_judges():
    config = load_models(FIXTURES / "models.yaml")
    assert config.judges == ["openai/gpt-4.1"]
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
uv run pytest tests/test_config.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'llm_weather.config'`

- [ ] **Step 4: Implement config module**

Create `src/llm_weather/config.py`:

```python
# ABOUTME: Loads and validates prompts.yaml and models.yaml configuration files.
# ABOUTME: Provides typed data structures for prompts, contestants, and judges.

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Prompt:
    id: str
    category: str
    prompt: str


@dataclass
class ModelsConfig:
    contestants: list[str]
    judges: list[str]


def load_prompts(path: Path) -> list[Prompt]:
    with open(path) as f:
        data = yaml.safe_load(f)
    return [Prompt(**p) for p in data["prompts"]]


def load_models(path: Path) -> ModelsConfig:
    with open(path) as f:
        data = yaml.safe_load(f)
    return ModelsConfig(
        contestants=[m["model"] for m in data["contestants"]],
        judges=[m["model"] for m in data["judges"]],
    )
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
uv run pytest tests/test_config.py -v
```

Expected: all 5 tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/llm_weather/config.py tests/test_config.py tests/fixtures/
git commit -m "feat: add config module for loading prompts and models YAML"
```

---

### Task 3: Runner Module

**Files:**
- Create: `src/llm_weather/runner.py`
- Create: `tests/test_runner.py`

The runner calls real LLM APIs via LiteLLM. Unit tests verify the response data structure using a single cheap model call. These tests require at least one API key to be set (e.g., `OPENAI_API_KEY`).

- [ ] **Step 1: Write failing tests**

Create `tests/test_runner.py`:

```python
# ABOUTME: Tests for the runner module that sends prompts to models.
# ABOUTME: Tests the response structure from real API calls.

import os
import json

import pytest

from llm_weather.runner import run_prompt, run_all
from llm_weather.config import Prompt

# Use cheapest available model for tests
TEST_MODEL = os.environ.get("LLM_WEATHER_TEST_MODEL", "openai/gpt-4.1-mini")

needs_api_key = pytest.mark.skipif(
    not any(os.environ.get(k) for k in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]),
    reason="No API key available",
)


@needs_api_key
def test_run_prompt_returns_expected_fields():
    result = run_prompt(TEST_MODEL, "What is 1 + 1?")
    assert "content" in result
    assert "latency_ms" in result
    assert "input_tokens" in result
    assert "output_tokens" in result
    assert isinstance(result["content"], str)
    assert len(result["content"]) > 0


@needs_api_key
def test_run_prompt_latency_is_positive():
    result = run_prompt(TEST_MODEL, "Say hello.")
    assert result["latency_ms"] > 0


@needs_api_key
def test_run_all_writes_responses_json(tmp_path):
    prompts = [Prompt(id="test-1", category="math", prompt="What is 1 + 1?")]
    contestants = [TEST_MODEL]
    result = run_all(prompts, contestants, tmp_path)

    assert (tmp_path / "responses.json").exists()
    assert result["run_id"] == tmp_path.name
    assert "test-1" in result["prompts"]
    assert TEST_MODEL in result["prompts"]["test-1"]["responses"]


@needs_api_key
def test_run_all_captures_errors_without_crashing(tmp_path):
    prompts = [Prompt(id="test-1", category="math", prompt="What is 1 + 1?")]
    contestants = [TEST_MODEL, "fake-provider/nonexistent-model"]
    result = run_all(prompts, contestants, tmp_path)

    # The valid model should have a response
    assert "content" in result["prompts"]["test-1"]["responses"][TEST_MODEL]
    # The fake model should have an error recorded
    fake_resp = result["prompts"]["test-1"]["responses"]["fake-provider/nonexistent-model"]
    assert "error" in fake_resp
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_runner.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'llm_weather.runner'`

- [ ] **Step 3: Implement runner module**

Create `src/llm_weather/runner.py`:

```python
# ABOUTME: Sends curated reasoning prompts to all contestant models via LiteLLM.
# ABOUTME: Collects responses with metadata and writes responses.json per run.

import json
import time
from datetime import datetime, timezone
from pathlib import Path

from litellm import completion

SYSTEM_PROMPT = "Answer the following question. Think step by step."


def run_prompt(model: str, prompt: str) -> dict:
    start = time.monotonic()
    response = completion(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    elapsed_ms = int((time.monotonic() - start) * 1000)
    choice = response.choices[0]
    usage = response.usage
    return {
        "content": choice.message.content,
        "latency_ms": elapsed_ms,
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
    }


def run_all(prompts: list, contestants: list[str], run_dir: Path) -> dict:
    results = {
        "run_id": run_dir.name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompts": {},
    }

    for p in prompts:
        results["prompts"][p.id] = {
            "prompt": p.prompt,
            "category": p.category,
            "responses": {},
        }
        for model in contestants:
            try:
                results["prompts"][p.id]["responses"][model] = run_prompt(
                    model, p.prompt
                )
            except Exception as e:
                results["prompts"][p.id]["responses"][model] = {
                    "error": str(e),
                }

    with open(run_dir / "responses.json", "w") as f:
        json.dump(results, f, indent=2)

    return results
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_runner.py -v
```

Expected: all 4 tests PASS (or skipped if no API key)

- [ ] **Step 5: Commit**

```bash
git add src/llm_weather/runner.py tests/test_runner.py
git commit -m "feat: add runner module for sending prompts to models"
```

---

### Task 4: Judge Module

**Files:**
- Create: `src/llm_weather/judge.py`
- Create: `tests/test_judge.py`

The judge module has two parts: pure logic (shuffle, format, vote counting) and API calls (sending to judge models). Unit tests cover the pure logic. Integration tests cover the API calls.

- [ ] **Step 1: Write failing tests for pure logic**

Create `tests/test_judge.py`:

```python
# ABOUTME: Tests for the blind judging module.
# ABOUTME: Tests shuffle logic, response formatting, and majority vote counting.

import os

import pytest

from llm_weather.judge import (
    shuffle_responses,
    format_responses,
    majority_winner,
    judge_prompt,
    judge_all,
)


def test_shuffle_responses_assigns_labels():
    responses = {
        "openai/gpt-4.1": {"content": "Answer A"},
        "anthropic/claude-sonnet-4-6": {"content": "Answer B"},
        "google/gemini-2.5-pro": {"content": "Answer C"},
    }
    label_to_model, label_to_content = shuffle_responses(responses)

    assert set(label_to_model.keys()) == {"A", "B", "C"}
    assert set(label_to_model.values()) == set(responses.keys())
    assert len(label_to_content) == 3
    assert all(isinstance(v, str) for v in label_to_content.values())


def test_shuffle_responses_content_matches():
    responses = {
        "model-a": {"content": "Alpha response"},
        "model-b": {"content": "Beta response"},
    }
    label_to_model, label_to_content = shuffle_responses(responses)

    for label, model in label_to_model.items():
        assert label_to_content[label] == responses[model]["content"]


def test_format_responses_includes_all_labels():
    label_to_content = {
        "A": "First answer",
        "B": "Second answer",
    }
    formatted = format_responses(label_to_content)

    assert "Response A:" in formatted
    assert "First answer" in formatted
    assert "Response B:" in formatted
    assert "Second answer" in formatted


def test_format_responses_sorted_by_label():
    label_to_content = {
        "C": "Third",
        "A": "First",
        "B": "Second",
    }
    formatted = format_responses(label_to_content)

    pos_a = formatted.index("Response A:")
    pos_b = formatted.index("Response B:")
    pos_c = formatted.index("Response C:")
    assert pos_a < pos_b < pos_c


def test_majority_winner_clear_majority():
    judge_results = {
        "judge-1": {"winner": "A", "ranking": ["A", "B", "C"], "reasoning": "..."},
        "judge-2": {"winner": "A", "ranking": ["A", "C", "B"], "reasoning": "..."},
        "judge-3": {"winner": "B", "ranking": ["B", "A", "C"], "reasoning": "..."},
    }
    assert majority_winner(judge_results) == "A"


def test_majority_winner_tie_returns_most_common():
    judge_results = {
        "judge-1": {"winner": "A", "ranking": ["A", "B"], "reasoning": "..."},
        "judge-2": {"winner": "B", "ranking": ["B", "A"], "reasoning": "..."},
        "judge-3": {"winner": "B", "ranking": ["B", "A"], "reasoning": "..."},
    }
    assert majority_winner(judge_results) == "B"


# Integration tests — require API keys
needs_api_key = pytest.mark.skipif(
    not any(os.environ.get(k) for k in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]),
    reason="No API key available",
)

TEST_JUDGE_MODEL = os.environ.get("LLM_WEATHER_TEST_MODEL", "openai/gpt-4.1-mini")


@needs_api_key
def test_judge_prompt_returns_verdict():
    label_to_content = {
        "A": "Yes, all bloops are lazzies. Since all bloops are razzies, and all razzies are lazzies, by transitivity all bloops are lazzies.",
        "B": "No, bloops are not lazzies because they are bloops.",
    }
    verdict = judge_prompt(
        "If all bloops are razzies and all razzies are lazzies, are all bloops lazzies?",
        label_to_content,
        TEST_JUDGE_MODEL,
    )
    assert "winner" in verdict
    assert verdict["winner"] in ("A", "B")
    assert "ranking" in verdict
    assert "reasoning" in verdict
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_judge.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'llm_weather.judge'`

- [ ] **Step 3: Implement judge module**

Create `src/llm_weather/judge.py`:

```python
# ABOUTME: Blindly evaluates contestant responses using multiple judge models.
# ABOUTME: Shuffles responses, assigns anonymous labels, and determines winners by majority vote.

import json
import random
import re
import string
from collections import Counter
from pathlib import Path

from litellm import completion

JUDGE_PROMPT = """Below are responses to a reasoning question. Rank them by quality of reasoning. Pick a winner and briefly explain why.

Question: {question}

{responses}

Respond in this exact JSON format and nothing else:
{{"winner": "<letter>", "ranking": ["<best>", "<next>", ...], "reasoning": "<one sentence>"}}"""


def shuffle_responses(responses: dict[str, dict]) -> tuple[dict[str, str], dict[str, str]]:
    models = list(responses.keys())
    random.shuffle(models)
    labels = list(string.ascii_uppercase[: len(models)])
    label_to_model = dict(zip(labels, models))
    label_to_content = {
        label: responses[model]["content"]
        for label, model in label_to_model.items()
    }
    return label_to_model, label_to_content


def format_responses(label_to_content: dict[str, str]) -> str:
    parts = []
    for label in sorted(label_to_content):
        parts.append(f"Response {label}:\n{label_to_content[label]}")
    return "\n\n".join(parts)


def parse_judge_response(text: str) -> dict:
    # Try to extract JSON from the response, handling markdown code fences
    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    raise ValueError(f"Could not parse judge response as JSON: {text}")


def judge_prompt(question: str, label_to_content: dict[str, str], judge_model: str) -> dict:
    formatted = format_responses(label_to_content)
    prompt = JUDGE_PROMPT.format(question=question, responses=formatted)
    response = completion(
        model=judge_model,
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.choices[0].message.content
    return parse_judge_response(content)


def majority_winner(judge_results: dict[str, dict]) -> str:
    winners = [r["winner"] for r in judge_results.values()]
    counts = Counter(winners)
    return counts.most_common(1)[0][0]


def judge_all(responses_data: dict, judges: list[str], run_dir: Path) -> dict:
    results = {"run_id": run_dir.name, "prompts": {}}

    for prompt_id, prompt_data in responses_data["prompts"].items():
        # Skip prompts where all responses errored
        valid_responses = {
            model: resp
            for model, resp in prompt_data["responses"].items()
            if "error" not in resp
        }
        if len(valid_responses) < 2:
            results["prompts"][prompt_id] = {
                "skipped": True,
                "reason": "fewer than 2 valid responses",
            }
            continue

        label_to_model, label_to_content = shuffle_responses(valid_responses)
        judge_verdicts = {}

        for judge_model in judges:
            try:
                verdict = judge_prompt(
                    prompt_data["prompt"], label_to_content, judge_model
                )
                judge_verdicts[judge_model] = verdict
            except Exception as e:
                judge_verdicts[judge_model] = {"error": str(e)}

        # Only count non-errored verdicts for majority
        valid_verdicts = {
            k: v for k, v in judge_verdicts.items() if "error" not in v
        }
        if valid_verdicts:
            winner_label = majority_winner(valid_verdicts)
            winner_model = label_to_model[winner_label]
        else:
            winner_label = None
            winner_model = None

        results["prompts"][prompt_id] = {
            "shuffle_mapping": label_to_model,
            "judges": judge_verdicts,
            "majority_winner": winner_label,
            "majority_winner_model": winner_model,
        }

    with open(run_dir / "judgments.json", "w") as f:
        json.dump(results, f, indent=2)

    return results
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_judge.py -v
```

Expected: all 6 pure-logic tests PASS, integration test PASS or skipped

- [ ] **Step 5: Commit**

```bash
git add src/llm_weather/judge.py tests/test_judge.py
git commit -m "feat: add blind multi-judge evaluation module"
```

---

### Task 5: Report Module

**Files:**
- Create: `src/llm_weather/report.py`
- Create: `tests/test_report.py`

All tests use constructed data — no API calls needed.

- [ ] **Step 1: Write failing tests**

Create `tests/test_report.py`:

```python
# ABOUTME: Tests for report generation (leaderboard, drift, markdown output).
# ABOUTME: Uses constructed data structures, no API calls needed.

from llm_weather.report import build_leaderboard, detect_drift, generate_summary, generate_detail


SAMPLE_JUDGMENTS = {
    "run_id": "2026-04-10T14-00-00",
    "prompts": {
        "logic-1": {
            "shuffle_mapping": {"A": "model-a", "B": "model-b"},
            "judges": {
                "judge-1": {"winner": "A", "ranking": ["A", "B"], "reasoning": "Better"},
            },
            "majority_winner": "A",
            "majority_winner_model": "model-a",
        },
        "math-1": {
            "shuffle_mapping": {"A": "model-a", "B": "model-b"},
            "judges": {
                "judge-1": {"winner": "B", "ranking": ["B", "A"], "reasoning": "Correct"},
            },
            "majority_winner": "B",
            "majority_winner_model": "model-b",
        },
        "code-1": {
            "shuffle_mapping": {"A": "model-a", "B": "model-b"},
            "judges": {
                "judge-1": {"winner": "A", "ranking": ["A", "B"], "reasoning": "Clearer"},
            },
            "majority_winner": "A",
            "majority_winner_model": "model-a",
        },
    },
}

SAMPLE_RESPONSES = {
    "run_id": "2026-04-10T14-00-00",
    "timestamp": "2026-04-10T14:00:00Z",
    "prompts": {
        "logic-1": {
            "prompt": "Test logic question?",
            "category": "logic",
            "responses": {
                "model-a": {"content": "Yes", "latency_ms": 100, "input_tokens": 10, "output_tokens": 5},
                "model-b": {"content": "No", "latency_ms": 200, "input_tokens": 10, "output_tokens": 3},
            },
        },
        "math-1": {
            "prompt": "Test math question?",
            "category": "math",
            "responses": {
                "model-a": {"content": "42", "latency_ms": 150, "input_tokens": 10, "output_tokens": 4},
                "model-b": {"content": "5", "latency_ms": 120, "input_tokens": 10, "output_tokens": 3},
            },
        },
        "code-1": {
            "prompt": "Test code question?",
            "category": "code",
            "responses": {
                "model-a": {"content": "result", "latency_ms": 180, "input_tokens": 15, "output_tokens": 8},
                "model-b": {"content": "output", "latency_ms": 160, "input_tokens": 15, "output_tokens": 6},
            },
        },
    },
}


def test_build_leaderboard_ranks_by_wins():
    leaderboard = build_leaderboard(SAMPLE_JUDGMENTS)
    assert leaderboard[0]["model"] == "model-a"
    assert leaderboard[0]["wins"] == 2
    assert leaderboard[0]["rank"] == 1
    assert leaderboard[1]["model"] == "model-b"
    assert leaderboard[1]["wins"] == 1
    assert leaderboard[1]["rank"] == 2


def test_build_leaderboard_total_is_prompt_count():
    leaderboard = build_leaderboard(SAMPLE_JUDGMENTS)
    assert leaderboard[0]["total"] == 3


def test_detect_drift_no_previous():
    current = [{"model": "model-a", "rank": 1}]
    drift = detect_drift(current, None)
    assert drift == []


def test_detect_drift_detects_rank_change():
    current = [
        {"model": "model-a", "rank": 1},
        {"model": "model-b", "rank": 2},
    ]
    previous = [
        {"model": "model-a", "rank": 2},
        {"model": "model-b", "rank": 1},
    ]
    drift = detect_drift(current, previous)
    assert len(drift) == 2
    model_a_drift = next(d for d in drift if d["model"] == "model-a")
    assert model_a_drift["direction"] == "↑"
    assert model_a_drift["change"] == 1


def test_detect_drift_no_change():
    current = [{"model": "model-a", "rank": 1}]
    previous = [{"model": "model-a", "rank": 1}]
    drift = detect_drift(current, previous)
    assert drift == []


def test_generate_summary_contains_leaderboard():
    leaderboard = build_leaderboard(SAMPLE_JUDGMENTS)
    summary = generate_summary(leaderboard, [], "2026-04-10T14-00-00")
    assert "model-a" in summary
    assert "model-b" in summary
    assert "2/3" in summary  # model-a wins
    assert "1/3" in summary  # model-b wins


def test_generate_summary_contains_drift():
    leaderboard = build_leaderboard(SAMPLE_JUDGMENTS)
    drift = [{"model": "model-b", "direction": "↓", "change": 1, "was": 1, "now": 2}]
    summary = generate_summary(leaderboard, drift, "2026-04-10T14-00-00")
    assert "↓" in summary
    assert "model-b" in summary


def test_generate_detail_contains_prompt_breakdowns():
    detail = generate_detail(SAMPLE_JUDGMENTS, SAMPLE_RESPONSES)
    assert "logic-1" in detail
    assert "math-1" in detail
    assert "code-1" in detail
    assert "model-a" in detail
    assert "model-b" in detail
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_report.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'llm_weather.report'`

- [ ] **Step 3: Implement report module**

Create `src/llm_weather/report.py`:

```python
# ABOUTME: Generates summary.md (leaderboard + drift) and detail.md (per-prompt breakdowns).
# ABOUTME: Compares against previous runs to detect ranking changes.

from collections import Counter
from pathlib import Path


def build_leaderboard(judgments: dict) -> list[dict]:
    wins = Counter()
    for prompt_data in judgments["prompts"].values():
        if prompt_data.get("skipped"):
            continue
        winner = prompt_data.get("majority_winner_model")
        if winner:
            wins[winner] += 1

    total = sum(
        1 for p in judgments["prompts"].values() if not p.get("skipped")
    )
    leaderboard = []
    for rank, (model, win_count) in enumerate(wins.most_common(), 1):
        leaderboard.append(
            {"rank": rank, "model": model, "wins": win_count, "total": total}
        )
    return leaderboard


def detect_drift(
    current_leaderboard: list[dict], previous_leaderboard: list[dict] | None
) -> list[dict]:
    if not previous_leaderboard:
        return []

    prev_ranks = {entry["model"]: entry["rank"] for entry in previous_leaderboard}
    drift = []
    for entry in current_leaderboard:
        model = entry["model"]
        if model in prev_ranks:
            change = prev_ranks[model] - entry["rank"]
            if change != 0:
                drift.append(
                    {
                        "model": model,
                        "direction": "↑" if change > 0 else "↓",
                        "change": abs(change),
                        "was": prev_ranks[model],
                        "now": entry["rank"],
                    }
                )
    return drift


def generate_summary(
    leaderboard: list[dict], drift: list[dict], run_id: str
) -> str:
    lines = [f"# LLM Weather Report — {run_id}", "", "## Leaderboard", ""]
    lines.append("| Rank | Model | Wins |")
    lines.append("|------|-------|------|")
    for entry in leaderboard:
        lines.append(
            f"| {entry['rank']} | {entry['model']} | {entry['wins']}/{entry['total']} |"
        )

    if drift:
        lines.append("")
        lines.append("## Drift")
        lines.append("")
        for d in drift:
            lines.append(
                f"- {d['model']}: {d['direction']} moved {d['change']} "
                f"(was #{d['was']}, now #{d['now']})"
            )

    lines.append("")
    return "\n".join(lines)


def generate_detail(judgments: dict, responses: dict) -> str:
    lines = [
        f"# LLM Weather Report — Detail — {judgments['run_id']}",
        "",
    ]

    for prompt_id, j_data in judgments["prompts"].items():
        if j_data.get("skipped"):
            lines.append(f"## {prompt_id}")
            lines.append(f"Skipped: {j_data['reason']}")
            lines.append("")
            continue

        r_data = responses["prompts"][prompt_id]
        lines.append(f"## {prompt_id}")
        lines.append("")
        lines.append(f"**Prompt:** {r_data['prompt']}")
        lines.append("")
        lines.append(
            f"**Winner:** {j_data['majority_winner_model']} "
            f"(label {j_data['majority_winner']})"
        )
        lines.append("")

        # Judge reasoning
        lines.append("### Judge Verdicts")
        lines.append("")
        for judge_model, verdict in j_data["judges"].items():
            if "error" in verdict:
                lines.append(f"- **{judge_model}:** Error — {verdict['error']}")
            else:
                lines.append(
                    f"- **{judge_model}:** Winner={verdict['winner']} — "
                    f"{verdict['reasoning']}"
                )
        lines.append("")

        # Model responses
        lines.append("### Responses")
        lines.append("")
        for model, resp in r_data["responses"].items():
            if "error" in resp:
                lines.append(f"**{model}:** Error — {resp['error']}")
            else:
                lines.append(f"**{model}** ({resp['latency_ms']}ms, {resp['output_tokens']} tokens):")
                lines.append("")
                lines.append(f"> {resp['content']}")
            lines.append("")

    return "\n".join(lines)


def write_reports(
    judgments: dict,
    responses: dict,
    leaderboard: list[dict],
    drift: list[dict],
    run_dir: Path,
) -> None:
    summary = generate_summary(leaderboard, drift, judgments["run_id"])
    detail = generate_detail(judgments, responses)
    (run_dir / "summary.md").write_text(summary)
    (run_dir / "detail.md").write_text(detail)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_report.py -v
```

Expected: all 8 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/llm_weather/report.py tests/test_report.py
git commit -m "feat: add report generation with leaderboard and drift detection"
```

---

### Task 6: Hugo Content Generator

**Files:**
- Create: `src/llm_weather/hugo.py`
- Create: `tests/test_hugo.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_hugo.py`:

```python
# ABOUTME: Tests for Hugo content page generation from run data.
# ABOUTME: Verifies frontmatter and body content of generated markdown files.

import yaml

from llm_weather.hugo import generate_hugo_content, write_hugo_page


SAMPLE_LEADERBOARD = [
    {"rank": 1, "model": "model-a", "wins": 3, "total": 5},
    {"rank": 2, "model": "model-b", "wins": 2, "total": 5},
]

SAMPLE_DRIFT = [
    {"model": "model-b", "direction": "↓", "change": 1, "was": 1, "now": 2},
]


def test_generate_hugo_content_has_frontmatter():
    content = generate_hugo_content(
        run_id="2026-04-10T14-00-00",
        leaderboard=SAMPLE_LEADERBOARD,
        drift=SAMPLE_DRIFT,
    )
    assert content.startswith("---\n")
    parts = content.split("---\n", 2)
    frontmatter = yaml.safe_load(parts[1])
    assert frontmatter["title"] == "2026-04-10T14-00-00"
    assert frontmatter["top_model"] == "model-a"


def test_generate_hugo_content_has_leaderboard_in_body():
    content = generate_hugo_content(
        run_id="2026-04-10T14-00-00",
        leaderboard=SAMPLE_LEADERBOARD,
        drift=[],
    )
    assert "model-a" in content
    assert "3/5" in content


def test_generate_hugo_content_has_drift():
    content = generate_hugo_content(
        run_id="2026-04-10T14-00-00",
        leaderboard=SAMPLE_LEADERBOARD,
        drift=SAMPLE_DRIFT,
    )
    assert "↓" in content
    assert "model-b" in content


def test_write_hugo_page_creates_file(tmp_path):
    content = generate_hugo_content(
        run_id="2026-04-10T14-00-00",
        leaderboard=SAMPLE_LEADERBOARD,
        drift=[],
    )
    site_dir = tmp_path / "site"
    write_hugo_page(content, "2026-04-10T14-00-00", site_dir)

    page_path = site_dir / "content" / "runs" / "2026-04-10T14-00-00.md"
    assert page_path.exists()
    assert "model-a" in page_path.read_text()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_hugo.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'llm_weather.hugo'`

- [ ] **Step 3: Implement Hugo content generator**

Create `src/llm_weather/hugo.py`:

```python
# ABOUTME: Generates Hugo-compatible markdown content pages from run data.
# ABOUTME: Creates pages with YAML frontmatter for the Hugo static site.

from pathlib import Path

import yaml


def generate_hugo_content(
    run_id: str,
    leaderboard: list[dict],
    drift: list[dict],
) -> str:
    frontmatter = {
        "title": run_id,
        "date": run_id.replace("T", " ").replace("-", ":", 3),
        "top_model": leaderboard[0]["model"] if leaderboard else "none",
        "leaderboard": leaderboard,
        "drift": drift,
    }

    lines = ["---"]
    lines.append(yaml.dump(frontmatter, default_flow_style=False).strip())
    lines.append("---")
    lines.append("")
    lines.append("## Leaderboard")
    lines.append("")
    lines.append("| Rank | Model | Wins |")
    lines.append("|------|-------|------|")
    for entry in leaderboard:
        lines.append(
            f"| {entry['rank']} | {entry['model']} | {entry['wins']}/{entry['total']} |"
        )

    if drift:
        lines.append("")
        lines.append("## Drift")
        lines.append("")
        for d in drift:
            lines.append(
                f"- {d['model']}: {d['direction']} moved {d['change']} "
                f"(was #{d['was']}, now #{d['now']})"
            )

    lines.append("")
    return "\n".join(lines)


def write_hugo_page(content: str, run_id: str, site_dir: Path) -> Path:
    runs_dir = site_dir / "content" / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    page_path = runs_dir / f"{run_id}.md"
    page_path.write_text(content)
    return page_path
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_hugo.py -v
```

Expected: all 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/llm_weather/hugo.py tests/test_hugo.py
git commit -m "feat: add Hugo content page generation from run data"
```

---

### Task 7: CLI

**Files:**
- Create: `src/llm_weather/cli.py`
- Create: `src/llm_weather/__main__.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_cli.py`:

```python
# ABOUTME: Tests for the CLI entry point using Click's test runner.
# ABOUTME: Tests command registration and help output.

from click.testing import CliRunner

from llm_weather.cli import main


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.output
    assert "report" in result.output
    assert "publish" in result.output


def test_cli_run_help():
    runner = CliRunner()
    result = runner.invoke(main, ["run", "--help"])
    assert result.exit_code == 0


def test_cli_report_help():
    runner = CliRunner()
    result = runner.invoke(main, ["report", "--help"])
    assert result.exit_code == 0
    assert "run-dir" in result.output.lower() or "RUN_DIR" in result.output


def test_cli_publish_help():
    runner = CliRunner()
    result = runner.invoke(main, ["publish", "--help"])
    assert result.exit_code == 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_cli.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'llm_weather.cli'`

- [ ] **Step 3: Implement CLI**

Create `src/llm_weather/cli.py`:

```python
# ABOUTME: Click-based CLI entry point for the LLM Weather Report tool.
# ABOUTME: Provides run, report, and publish commands.

import json
from datetime import datetime, timezone
from pathlib import Path

import click

from llm_weather.config import load_models, load_prompts
from llm_weather.hugo import generate_hugo_content, write_hugo_page
from llm_weather.judge import judge_all
from llm_weather.report import (
    build_leaderboard,
    detect_drift,
    write_reports,
)
from llm_weather.runner import run_all

def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent


def find_previous_run(runs_dir: Path, current_run_id: str) -> dict | None:
    if not runs_dir.exists():
        return None
    run_dirs = sorted(
        [d for d in runs_dir.iterdir() if d.is_dir() and d.name != current_run_id]
    )
    if not run_dirs:
        return None
    prev_dir = run_dirs[-1]
    judgments_path = prev_dir / "judgments.json"
    if not judgments_path.exists():
        return None
    with open(judgments_path) as f:
        prev_judgments = json.load(f)
    return build_leaderboard(prev_judgments)


@click.group()
@click.option(
    "--project-root",
    default=None,
    type=click.Path(exists=True),
    help="Project root directory (default: auto-detect).",
)
@click.pass_context
def main(ctx, project_root):
    """LLM Weather Report — track reasoning capability drift across models."""
    ctx.ensure_object(dict)
    ctx.obj["project_root"] = Path(project_root) if project_root else get_project_root()


@main.command()
@click.option(
    "--prompts",
    default=None,
    type=click.Path(exists=True),
    help="Path to prompts YAML file.",
)
@click.option(
    "--models",
    default=None,
    type=click.Path(exists=True),
    help="Path to models YAML file.",
)
@click.pass_context
def run(ctx, prompts, models):
    """Execute a full run: prompt models, judge responses, generate reports."""
    root = ctx.obj["project_root"]
    prompts_path = Path(prompts) if prompts else root / "prompts.yaml"
    models_path = Path(models) if models else root / "models.yaml"
    prompts_config = load_prompts(prompts_path)
    models_config = load_models(models_path)

    run_id = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    runs_dir = root / "runs"
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=True)

    click.echo(f"Starting run {run_id}")
    click.echo(f"  Prompts: {len(prompts_config)}")
    click.echo(f"  Contestants: {len(models_config.contestants)}")
    click.echo(f"  Judges: {len(models_config.judges)}")

    # Step 1: Run prompts
    click.echo("\nRunning prompts...")
    responses = run_all(prompts_config, models_config.contestants, run_dir)

    # Step 2: Judge
    click.echo("Judging responses...")
    judgments = judge_all(responses, models_config.judges, run_dir)

    # Step 3: Reports
    click.echo("Generating reports...")
    leaderboard = build_leaderboard(judgments)
    previous = find_previous_run(runs_dir, run_id)
    drift = detect_drift(leaderboard, previous)
    write_reports(judgments, responses, leaderboard, drift, run_dir)

    # Step 4: Hugo content
    click.echo("Generating Hugo content...")
    hugo_content = generate_hugo_content(run_id, leaderboard, drift)
    site_dir = root / "site"
    write_hugo_page(hugo_content, run_id, site_dir)

    click.echo(f"\nDone! Results in {run_dir}")


@main.command()
@click.argument("run_dir", type=click.Path(exists=True))
def report(run_dir):
    """Regenerate reports from existing run data."""
    run_dir = Path(run_dir)
    with open(run_dir / "responses.json") as f:
        responses = json.load(f)
    with open(run_dir / "judgments.json") as f:
        judgments = json.load(f)

    leaderboard = build_leaderboard(judgments)
    runs_dir = run_dir.parent
    previous = find_previous_run(runs_dir, run_dir.name)
    drift = detect_drift(leaderboard, previous)
    write_reports(judgments, responses, leaderboard, drift, run_dir)
    click.echo(f"Reports regenerated in {run_dir}")


@main.command()
@click.pass_context
def publish(ctx):
    """Regenerate all Hugo content from runs/ and build the site."""
    root = ctx.obj["project_root"]
    runs_dir = root / "runs"
    site_dir = root / "site"

    if not runs_dir.exists():
        click.echo("No runs directory found.")
        return

    run_dirs = sorted([d for d in runs_dir.iterdir() if d.is_dir()])
    for run_dir in run_dirs:
        judgments_path = run_dir / "judgments.json"
        if not judgments_path.exists():
            continue

        with open(judgments_path) as f:
            judgments = json.load(f)

        leaderboard = build_leaderboard(judgments)
        previous = find_previous_run(runs_dir, run_dir.name)
        drift = detect_drift(leaderboard, previous)
        hugo_content = generate_hugo_content(run_dir.name, leaderboard, drift)
        write_hugo_page(hugo_content, run_dir.name, site_dir)

    click.echo(f"Hugo content generated for {len(run_dirs)} runs in {site_dir}")
```

Create `src/llm_weather/__main__.py`:

```python
# ABOUTME: Allows running the package with `python -m llm_weather`.
# ABOUTME: Delegates to the Click CLI entry point.

from llm_weather.cli import main

main()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_cli.py -v
```

Expected: all 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/llm_weather/cli.py src/llm_weather/__main__.py tests/test_cli.py
git commit -m "feat: add CLI with run, report, and publish commands"
```

---

### Task 8: Hugo Site Templates

**Files:**
- Create: `site/hugo.toml`
- Create: `site/layouts/_default/baseof.html`
- Create: `site/layouts/_default/list.html`
- Create: `site/layouts/runs/single.html`

No tests for this task — it's static template files. Hugo's build verifies correctness.

- [ ] **Step 1: Create Hugo config**

Create `site/hugo.toml`:

```toml
baseURL = "/"
languageCode = "en-us"
title = "LLM Weather Report"

[params]
  description = "Tracking reasoning capability drift across LLM models"
```

- [ ] **Step 2: Create base template**

Create `site/layouts/_default/baseof.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ .Title }} — LLM Weather Report</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      max-width: 800px;
      margin: 2rem auto;
      padding: 0 1rem;
      color: #1a1a1a;
      line-height: 1.6;
    }
    h1, h2 { border-bottom: 1px solid #e5e5e5; padding-bottom: 0.3rem; }
    table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
    th, td { border: 1px solid #ddd; padding: 0.5rem 1rem; text-align: left; }
    th { background: #f5f5f5; }
    a { color: #0066cc; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .nav { margin-bottom: 2rem; font-size: 0.9rem; }
    .drift-up { color: #22863a; }
    .drift-down { color: #cb2431; }
  </style>
</head>
<body>
  <div class="nav"><a href="/">← LLM Weather Report</a></div>
  {{ block "main" . }}{{ end }}
</body>
</html>
```

- [ ] **Step 3: Create index/list template**

Create `site/layouts/_default/list.html`:

```html
{{ define "main" }}
<h1>LLM Weather Report</h1>
<p>Tracking reasoning capability drift across LLM models.</p>

{{ $runs := where .Site.RegularPages "Section" "runs" }}
{{ $latest := index (sort $runs "Date" "desc") 0 }}

{{ with $latest }}
<h2>Current Forecast</h2>
<p>Latest run: <a href="{{ .RelPermalink }}">{{ .Title }}</a></p>

{{ .Content }}
{{ end }}

<h2>Past Reports</h2>
<ul>
{{ range sort $runs "Date" "desc" }}
  <li>
    <a href="{{ .RelPermalink }}">{{ .Title }}</a>
    — Top model: {{ .Params.top_model }}
  </li>
{{ end }}
</ul>
{{ end }}
```

- [ ] **Step 4: Create run detail template**

Create `site/layouts/runs/single.html`:

```html
{{ define "main" }}
<h1>Run: {{ .Title }}</h1>

{{ .Content }}

{{ with .Params.drift }}
<h2>Drift</h2>
<ul>
{{ range . }}
  <li>
    <span class="{{ if eq .direction "↑" }}drift-up{{ else }}drift-down{{ end }}">
      {{ .direction }}
    </span>
    {{ .model }}: moved {{ .change }} (was #{{ .was }}, now #{{ .now }})
  </li>
{{ end }}
</ul>
{{ end }}
{{ end }}
```

- [ ] **Step 5: Verify Hugo builds**

```bash
which hugo || brew install hugo
cd /Users/harper/Public/src/2389/llm-weather/site && hugo --printPathWarnings 2>&1; cd ..
```

Expected: builds with no errors (may warn about no content, which is fine)

- [ ] **Step 6: Commit**

```bash
git add site/
git commit -m "feat: add Hugo site templates for weather report"
```

---

### Task 9: GitHub Actions Workflow

**Files:**
- Create: `.github/workflows/weather.yml`

- [ ] **Step 1: Create workflow file**

Create `.github/workflows/weather.yml`:

```yaml
name: LLM Weather Report

on:
  schedule:
    # 5am, 8am, 12pm, 5pm, 8pm, 12am CT (UTC-5 CDT)
    - cron: '0 1,5,10,13,17,22 * * *'
  workflow_dispatch: {}

permissions:
  contents: write

jobs:
  weather:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v5

      - run: uv python install

      - run: uv sync --locked

      - name: Run LLM Weather
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
        run: uv run llm-weather run

      - name: Build Hugo site
        uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: 'latest'

      - run: cd site && hugo --minify

      - name: Commit results
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add runs/ site/content/ site/public/
          git diff --cached --quiet || git commit -m "chore: weather report $(date -u +%Y-%m-%dT%H-%M-%S)"
          git push
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/weather.yml
git commit -m "feat: add GitHub Actions workflow for scheduled runs"
```

---

### Task 10: End-to-End Integration Test

**Files:**
- Create: `tests/test_e2e.py`

This test runs the full pipeline with real API calls against a minimal config (1 prompt, 1 contestant, 1 judge).

- [ ] **Step 1: Write e2e test**

Create `tests/test_e2e.py`:

```python
# ABOUTME: End-to-end integration test for the full LLM Weather pipeline.
# ABOUTME: Runs one prompt through one model, judges it, and generates reports.

import json
import os

import pytest
from click.testing import CliRunner

from llm_weather.cli import main

needs_api_key = pytest.mark.skipif(
    not any(os.environ.get(k) for k in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]),
    reason="No API key available",
)

TEST_MODEL = os.environ.get("LLM_WEATHER_TEST_MODEL", "openai/gpt-4.1-mini")


@needs_api_key
def test_full_pipeline(tmp_path):
    # Create minimal config files
    prompts_file = tmp_path / "prompts.yaml"
    prompts_file.write_text(
        "prompts:\n"
        "  - id: e2e-test\n"
        "    category: math\n"
        '    prompt: "What is 2 + 2?"\n'
    )

    models_file = tmp_path / "models.yaml"
    models_file.write_text(
        f"contestants:\n"
        f"  - model: {TEST_MODEL}\n"
        f"judges:\n"
        f"  - model: {TEST_MODEL}\n"
    )

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--project-root", str(tmp_path),
            "run",
            "--prompts", str(prompts_file),
            "--models", str(models_file),
        ],
    )

    assert result.exit_code == 0, f"CLI failed: {result.output}"
    assert "Done!" in result.output

    # Verify run directory was created with expected files
    runs_dir = tmp_path / "runs"
    assert runs_dir.exists()
    run_dirs = list(runs_dir.iterdir())
    assert len(run_dirs) == 1

    run_dir = run_dirs[0]
    assert (run_dir / "responses.json").exists()
    assert (run_dir / "judgments.json").exists()
    assert (run_dir / "summary.md").exists()
    assert (run_dir / "detail.md").exists()

    # Verify Hugo content was generated
    hugo_content_dir = tmp_path / "site" / "content" / "runs"
    assert hugo_content_dir.exists()
    assert len(list(hugo_content_dir.iterdir())) == 1
```

- [ ] **Step 2: Run the e2e test**

```bash
uv run pytest tests/test_e2e.py -v
```

Expected: PASS (or skipped if no API key)

- [ ] **Step 3: Run full test suite**

```bash
uv run pytest tests/ -v
```

Expected: all tests PASS

- [ ] **Step 4: Commit**

```bash
git add tests/test_e2e.py
git commit -m "test: add end-to-end integration test for full pipeline"
```
