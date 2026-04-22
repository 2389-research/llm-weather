# LLM Weather Report — 2026-04-22T01-42-01

## Drift Alerts

- openai/gpt-5.4-mini | spatial-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-flash | causality-1 | SCORE_RISE: 3.67 → 5.0
- gemini/gemini-2.5-flash | common-sense-1 | SCORE_DROP: 4.83 → 3.67

## Scorecard

| Model | logic-1 | math-1 | spatial-1 | causality-1 | code-1 | ambiguity-1 | common-sense-1 |
|-------|------|------|------|------|------|------|------|
| anthropic/claude-haiku-4-5 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.83) | ✓ (4.67) | ✓ (4.33) | ✓ (3.33) |
| anthropic/claude-opus-4-6 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.67) | ✓ (4.67) | ✓ (5.0) | ✓ (4.33) |
| anthropic/claude-sonnet-4-6 | ✓ (5.0) | ✓ (5.0) | ✓ (4.83) | ✓ (4.67) | ✓ (4.67) | ✓ (4.5) | ✓ (3.33) |
| gemini/gemini-2.5-flash | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.83) | ✓ (4.5) | ✓ (3.67) |
| gemini/gemini-2.5-pro | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.67) | ✓ (4.67) | ✓ (4.67) | ✓ (5.0) |
| ollama/llama3 | — | — | — | — | — | — | — |
| openai/gpt-5.4 | ✓ (4.67) | ✓ (5.0) | ✓ (5.0) | ✓ (4.83) | ✓ (4.83) | ✓ (4.33) | ✓ (4.5) |
| openai/gpt-5.4-mini | ✓ (4.5) | ✓ (5.0) | ✗ (3.83) | ✓ (4.5) | ✓ (4.67) | ✓ (4.5) | ✓ (4.33) |
