# LLM Weather Report — 2026-04-15T05-47-16

## Drift Alerts

- openai/gpt-5.4-mini | spatial-1 | REGRESSION: correct → incorrect
- gemini/gemini-2.5-pro | causality-1 | IMPROVEMENT: incorrect → correct
- gemini/gemini-2.5-pro | ambiguity-1 | IMPROVEMENT: incorrect → correct
- gemini/gemini-2.5-pro | common-sense-1 | IMPROVEMENT: incorrect → correct
- gemini/gemini-2.5-flash | causality-1 | IMPROVEMENT: incorrect → correct

## Scorecard

| Model | logic-1 | math-1 | spatial-1 | causality-1 | code-1 | ambiguity-1 | common-sense-1 |
|-------|------|------|------|------|------|------|------|
| anthropic/claude-haiku-4-5 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.5) | ✓ (4.67) | ✓ (4.5) | ✓ (3.2) |
| anthropic/claude-opus-4-6 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.8) | ✓ (4.83) | ✓ (5.0) | ✓ (4.4) |
| anthropic/claude-sonnet-4-6 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.8) | ✓ (4.5) | ✓ (4.33) | ✓ (3.67) |
| gemini/gemini-2.5-flash | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (3.6) | ✓ (4.83) | ✓ (4.67) | ✓ (3.6) |
| gemini/gemini-2.5-pro | ✓ (5.0) | ✓ (5.0) | ✓ (4.83) | ✓ (4.5) | ✓ (4.67) | ✓ (5.0) | ✓ (5.0) |
| ollama/llama3 | — | — | — | — | — | — | — |
| openai/gpt-5.4 | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (5.0) | ✓ (4.8) | ✓ (4.6) | ✓ (4.5) |
| openai/gpt-5.4-mini | ✓ (5.0) | ✓ (5.0) | ✗ (3.6) | ✓ (4.6) | ✓ (4.6) | ✓ (4.8) | ✓ (4.5) |
