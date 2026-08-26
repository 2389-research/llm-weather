# LLM Weather Report — 2026-08-26T05-14-06

## Drift Alerts

- openai/gpt-5.4-mini | spatial-1 | SCORE_DROP: 3.5 → 2.0
- anthropic/claude-haiku-4-5 | common-sense-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-pro | logic-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-pro | math-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-pro | spatial-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-pro | causality-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-pro | code-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-pro | ambiguity-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-pro | common-sense-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-flash | logic-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-flash | math-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-flash | spatial-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-flash | causality-1 | IMPROVEMENT: incorrect → incorrect
- gemini/gemini-2.5-flash | code-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-flash | ambiguity-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-flash | common-sense-1 | REGRESSION: correct → incorrect

## Scorecard

| Model | logic-1 | math-1 | spatial-1 | causality-1 | code-1 | ambiguity-1 | common-sense-1 |
|-------|------|------|------|------|------|------|------|
| anthropic/claude-haiku-4-5 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.5) | ✓ (5.0) | ✓ (4.5) | ✗ (3.0) |
| anthropic/claude-opus-4-6 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.75) | ✓ (5.0) | ✓ (5.0) | ✓ (4.5) |
| anthropic/claude-sonnet-4-6 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.5) | ✓ (4.25) |
| gemini/gemini-2.5-flash | — | — | — | — | — | — | — |
| gemini/gemini-2.5-pro | — | — | — | — | — | — | — |
| ollama/llama3 | — | — | — | — | — | — | — |
| openai/gpt-5.4 | ✓ (4.5) | ✓ (4.5) | ✓ (5.0) | ✓ (4.75) | ✓ (5.0) | ✓ (4.5) | ✓ (4.75) |
| openai/gpt-5.4-mini | ✓ (5.0) | ✓ (5.0) | ✗ (2.0) | ✓ (4.75) | ✓ (4.75) | ✓ (4.75) | ✓ (4.75) |
