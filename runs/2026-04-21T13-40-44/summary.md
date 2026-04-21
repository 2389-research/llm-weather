# LLM Weather Report — 2026-04-21T13-40-44

## Drift Alerts

- openai/gpt-5.4 | math-1 | SCORE_DROP: 5.0 → 3.8
- anthropic/claude-sonnet-4-6 | common-sense-1 | REGRESSION: correct → incorrect
- anthropic/claude-haiku-4-5 | common-sense-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-flash | causality-1 | REGRESSION: correct → incorrect

## Scorecard

| Model | logic-1 | math-1 | spatial-1 | causality-1 | code-1 | ambiguity-1 | common-sense-1 |
|-------|------|------|------|------|------|------|------|
| anthropic/claude-haiku-4-5 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.67) | ✓ (5.0) | ✓ (4.4) | ✗ (2.75) |
| anthropic/claude-opus-4-6 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.8) | ✓ (4.8) | ✓ (5.0) | ✓ (4.5) |
| anthropic/claude-sonnet-4-6 | ✓ (4.8) | ✓ (5.0) | ✓ (5.0) | ✓ (4.6) | ✓ (4.5) | ✓ (4.33) | ✗ (3.0) |
| gemini/gemini-2.5-flash | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✗ (1.6) | ✓ (4.8) | ✓ (4.6) | ✓ (4.5) |
| gemini/gemini-2.5-pro | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.5) | ✓ (5.0) |
| ollama/llama3 | — | — | — | — | — | — | — |
| openai/gpt-5.4 | ✓ (4.75) | ✓ (3.8) | ✓ (5.0) | ✓ (4.75) | ✓ (4.67) | ✓ (4.33) | ✓ (4.4) |
| openai/gpt-5.4-mini | ✓ (5.0) | ✓ (5.0) | ✗ (3.83) | ✓ (4.8) | ✓ (4.8) | ✓ (4.5) | ✓ (4.33) |
