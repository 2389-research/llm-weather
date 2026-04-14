---
title: "LLM Weather Report"
---

Model providers push updates all the time. Weight tweaks, system prompt changes, quantization experiments, infrastructure swaps. Almost none of it gets announced. You just wake up one morning and GPT handles a logic puzzle differently than it did last week.

We got tired of not knowing when this happened. So we built something simple: six times a day, we send the same seven reasoning prompts to a handful of major models and score what comes back. Same prompts, same grading, every four hours. When something changes, we publish it here.

This isn't a leaderboard. We don't care which model is "best." We care whether each model is the same as it was yesterday. Think of it as a weather report: not a competition, just a reading of current conditions.

We also test the raw endpoint, not an agent stack. One system prompt, one user message, one API call. No tools, no retrieval, no chain-of-thought scaffolding. If a model starts failing a basic syllogism, that's the model, not some middleware bug.

Everything is open. Raw responses, judge verdicts, scorecard data, source code. If you want to check our work or run your own analysis, it's all on [GitHub](https://github.com/2389-research/llm-weather).
