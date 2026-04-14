# LLM Weather Report — 2026-04-14T13-40-46

## Drift Alerts

- gemini/gemini-2.5-pro | math-1 | IMPROVEMENT: incorrect → correct
- gemini/gemini-2.5-pro | code-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-pro | common-sense-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-flash | causality-1 | IMPROVEMENT: incorrect → correct
- gemini/gemini-2.5-flash | common-sense-1 | IMPROVEMENT: incorrect → correct

## Scorecard

| Model | logic-1 | math-1 | spatial-1 | causality-1 | code-1 | ambiguity-1 | common-sense-1 |
|-------|------|------|------|------|------|------|------|
| anthropic/claude-haiku-4-5 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.67) | ✓ (4.8) | ✓ (4.33) | ✓ (3.33) |
| anthropic/claude-opus-4-6 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.67) | ✓ (5.0) | ✓ (4.4) |
| anthropic/claude-sonnet-4-6 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.75) | ✓ (4.8) | ✓ (4.0) |
| gemini/gemini-2.5-flash | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.8) | ✓ (4.6) | ✓ (4.8) |
| gemini/gemini-2.5-pro | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.83) | — | ✓ (4.6) | — |
| ollama/llama3 | — | — | — | — | — | — | — |
| openai/gpt-5.4 | ✓ (5.0) | ✓ (4.8) | ✓ (5.0) | ✓ (5.0) | ✓ (4.8) | ✓ (4.4) | ✓ (4.33) |
| openai/gpt-5.4-mini | ✓ (4.83) | ✓ (5.0) | ✗ (2.17) | ✓ (4.75) | ✓ (4.8) | ✓ (4.5) | ✓ (4.33) |
