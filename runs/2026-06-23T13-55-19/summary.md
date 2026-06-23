# LLM Weather Report — 2026-06-23T13-55-19

## Drift Alerts

- openai/gpt-5.4-mini | spatial-1 | SCORE_DROP: 3.67 → 2.25
- anthropic/claude-sonnet-4-6 | common-sense-1 | SCORE_RISE: 3.67 → 4.75
- anthropic/claude-haiku-4-5 | common-sense-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-flash | causality-1 | SCORE_DROP: 3.5 → 1.75

## Scorecard

| Model | logic-1 | math-1 | spatial-1 | causality-1 | code-1 | ambiguity-1 | common-sense-1 |
|-------|------|------|------|------|------|------|------|
| anthropic/claude-haiku-4-5 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.75) | ✓ (4.5) | ✓ (4.5) | ✗ (3.0) |
| anthropic/claude-opus-4-6 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.5) | ✓ (5.0) | ✓ (4.5) |
| anthropic/claude-sonnet-4-6 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.5) | ✓ (4.75) | ✓ (4.75) |
| gemini/gemini-2.5-flash | ✓ (4.67) | ✓ (5.0) | ✓ (5.0) | ✗ (1.75) | ✓ (4.75) | ✓ (4.5) | ✓ (3.75) |
| gemini/gemini-2.5-pro | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.75) | ✓ (4.75) | ✓ (4.75) |
| ollama/llama3 | — | — | — | — | — | — | — |
| openai/gpt-5.4 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.75) | ✓ (4.75) | ✓ (4.5) | ✓ (4.75) |
| openai/gpt-5.4-mini | ✓ (4.83) | ✓ (4.83) | ✗ (2.25) | ✓ (5.0) | ✓ (4.5) | ✓ (4.5) | ✓ (4.5) |
