# LLM Weather Report — 2026-04-12T17-16-41

## Drift Alerts

- gemini/gemini-2.5-pro | math-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-pro | causality-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-flash | causality-1 | SCORE_RISE: 1.33 → 3.33

## Scorecard

| Model | logic-1 | math-1 | spatial-1 | causality-1 | code-1 | ambiguity-1 | common-sense-1 |
|-------|------|------|------|------|------|------|------|
| anthropic/claude-haiku-4-5 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.6) | ✓ (4.8) | ✓ (4.5) | ✓ (3.2) |
| anthropic/claude-opus-4-6 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.8) | ✓ (4.8) | ✓ (5.0) | ✓ (4.33) |
| anthropic/claude-sonnet-4-6 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.8) | ✓ (4.83) | ✓ (4.33) | ✓ (3.2) |
| gemini/gemini-2.5-flash | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✗ (3.33) | ✓ (4.8) | ✓ (4.67) | ✓ (3.75) |
| gemini/gemini-2.5-pro | ✓ (5.0) | — | ✓ (5.0) | — | ✓ (4.67) | ✓ (4.83) | ✓ (4.67) |
| ollama/llama3 | — | — | — | — | — | — | — |
| openai/gpt-5.4 | ✓ (5.0) | ✓ (5.0) | ✓ (4.33) | ✓ (5.0) | ✓ (4.67) | ✓ (4.33) | ✓ (4.5) |
| openai/gpt-5.4-mini | ✓ (5.0) | ✓ (5.0) | ✗ (3.83) | ✓ (4.67) | ✓ (4.67) | ✓ (4.8) | ✓ (4.33) |
