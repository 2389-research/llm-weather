# LLM Weather Report — 2026-04-13T10-40-17

## Drift Alerts

- openai/gpt-5.4-mini | spatial-1 | SCORE_RISE: 2.4 → 3.4
- gemini/gemini-2.5-pro | spatial-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-pro | common-sense-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-flash | causality-1 | SCORE_RISE: 1.83 → 3.33

## Scorecard

| Model | logic-1 | math-1 | spatial-1 | causality-1 | code-1 | ambiguity-1 | common-sense-1 |
|-------|------|------|------|------|------|------|------|
| anthropic/claude-haiku-4-5 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.5) | ✓ (5.0) | ✓ (4.6) | ✓ (3.2) |
| anthropic/claude-opus-4-6 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.8) | ✓ (5.0) | ✓ (4.4) |
| anthropic/claude-sonnet-4-6 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.67) | ✓ (4.67) | ✓ (4.8) | ✓ (3.5) |
| gemini/gemini-2.5-flash | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✗ (3.33) | ✓ (5.0) | ✓ (4.67) | ✓ (4.0) |
| gemini/gemini-2.5-pro | ✓ (5.0) | ✓ (5.0) | — | ✓ (4.5) | ✓ (5.0) | ✓ (4.5) | — |
| ollama/llama3 | — | — | — | — | — | — | — |
| openai/gpt-5.4 | ✓ (4.75) | ✓ (4.8) | ✓ (5.0) | ✓ (4.83) | ✓ (5.0) | ✓ (4.83) | ✓ (4.5) |
| openai/gpt-5.4-mini | ✓ (4.8) | ✓ (4.83) | ✗ (3.4) | ✓ (5.0) | ✓ (4.8) | ✓ (4.67) | ✓ (4.0) |
