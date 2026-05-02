# LLM Weather Report — 2026-05-02T10-25-08

## Drift Alerts

- openai/gpt-5.4-mini | spatial-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-pro | logic-1 | IMPROVEMENT: incorrect → correct
- gemini/gemini-2.5-flash | causality-1 | REGRESSION: correct → incorrect

## Scorecard

| Model | logic-1 | math-1 | spatial-1 | causality-1 | code-1 | ambiguity-1 | common-sense-1 |
|-------|------|------|------|------|------|------|------|
| anthropic/claude-haiku-4-5 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.5) | ✓ (5.0) | ✓ (4.33) | ✓ (3.0) |
| anthropic/claude-opus-4-6 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.83) | ✓ (4.67) | ✓ (5.0) | ✓ (4.4) |
| anthropic/claude-sonnet-4-6 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.8) | ✓ (4.33) | ✓ (4.4) | ✓ (3.5) |
| gemini/gemini-2.5-flash | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✗ (2.33) | ✓ (4.8) | ✓ (4.8) | ✓ (3.8) |
| gemini/gemini-2.5-pro | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | — | — | ✓ (5.0) | ✓ (5.0) |
| ollama/llama3 | — | — | — | — | — | — | — |
| openai/gpt-5.4 | ✓ (5.0) | ✓ (4.8) | ✓ (5.0) | ✓ (5.0) | ✓ (4.67) | ✓ (4.4) | ✓ (4.67) |
| openai/gpt-5.4-mini | ✓ (5.0) | ✓ (4.6) | ✗ (1.75) | ✓ (4.6) | ✓ (4.6) | ✓ (4.8) | ✓ (4.4) |
