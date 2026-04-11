# Correctness Tracking — Design Spec

## Problem

The current system picks a "winner" per prompt via comparative judging, then builds a leaderboard. This measures which model is best *this run*, not whether any model's behavior changed from its baseline. The whole point of LLM Weather is drift detection, not ranking.

## Design

### Judge: Individual Correctness Evaluation

Replace comparative judging ("which response is best?") with individual evaluation ("is this response correct?").

For each model's response to each prompt, ask each judge:
- Is the response correct? (boolean)
- Rate reasoning quality 1-5
- One-sentence justification

Use 3 judges, majority vote on correctness. Average the scores.

**New judge prompt:**
```
Question: {question}
Response: {response}

Evaluate this response. Is it correct? Rate the reasoning quality from 1 (poor) to 5 (excellent).

Respond in this exact JSON format:
{"correct": true/false, "score": 1-5, "reasoning": "one sentence"}
```

**Output format (judgments.json):**
```json
{
  "run_id": "...",
  "prompts": {
    "logic-1": {
      "prompt": "...",
      "evaluations": {
        "openai/gpt-4.1": {
          "judges": {
            "judge-model-1": {"correct": true, "score": 5, "reasoning": "..."},
            "judge-model-2": {"correct": true, "score": 4, "reasoning": "..."},
            "judge-model-3": {"correct": true, "score": 5, "reasoning": "..."}
          },
          "majority_correct": true,
          "avg_score": 4.67
        }
      }
    }
  }
}
```

### Report: Scorecard + Drift Alerts

Replace leaderboard with a correctness scorecard.

**Scorecard:** model × prompt grid showing correctness and score.

```
## Scorecard

| Model          | logic-1 | math-1 | spatial-1 | ... |
|----------------|---------|--------|-----------|-----|
| openai/gpt-4.1 | ✓ (5.0) | ✓ (5.0) | ✓ (4.3)  | ... |
| claude-sonnet   | ✓ (4.0) | ✗ (2.0) | ✓ (5.0)  | ... |
```

**Drift:** Compare against previous run. Flag:
- Correctness flip: model went correct→incorrect or vice versa
- Score change: score changed by >= 1.0 point

```
## Drift Alerts

- anthropic/claude-sonnet-4-6 | math-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-flash | code-1 | IMPROVEMENT: incorrect → correct
- openai/gpt-4.1 | logic-1 | SCORE DROP: 5.0 → 3.7
```

### Hugo: Updated Templates

**Frontmatter:** Replace `top_model` and `leaderboard` with `scorecard` and `drift_alerts`.

**Index page:** Show latest scorecard + drift alerts, link to past runs.

**Detail page:** Show scorecard table, drift alerts, and per-prompt breakdowns.

### What Stays The Same

- `runner.py` — unchanged, still collects responses
- `config.py` — unchanged
- `prompts.yaml` / `models.yaml` — unchanged
- File structure: `runs/<run_id>/responses.json`, `judgments.json`, `summary.md`, `detail.md`
- CLI interface: `llm-weather run`, `llm-weather report`, `llm-weather publish`

### Files Changed

1. `judge.py` — new individual evaluation logic, new prompt, new output format
2. `report.py` — scorecard builder, drift detection on correctness/scores
3. `hugo.py` — new frontmatter structure, scorecard body
4. `site/layouts/_default/list.html` — show scorecard instead of leaderboard
5. `site/layouts/runs/single.html` — show scorecard + drift alerts
6. `tests/test_judge.py` — updated for new judge format
7. `tests/test_report.py` — updated for scorecard/drift
8. `tests/test_hugo.py` — updated for new frontmatter
