---
title: "LLM Weather Report"
---

Model providers ship updates constantly — weight adjustments, system prompt changes, quantization tweaks, infrastructure migrations. Most of these changes are silent. No changelog, no announcement. But they can alter how a model reasons.

The LLM Weather Report catches these changes. Six times a day, we send the same fixed set of reasoning prompts to major LLM endpoints and score the responses. When a model that correctly solved a logic puzzle yesterday starts failing today, we flag it. When reasoning quality degrades even though the answer is still technically correct, we flag that too.

This is not a benchmark or a leaderboard. We are not comparing models against each other. We are tracking whether each model stays consistent with itself over time — a weather report for reasoning capability, not a horse race.

Every evaluation hits the raw API endpoint directly. No agents, no tool use, no retrieval, no multi-turn conversation. Just a single system prompt ("Answer the following question. Think step by step.") and one user message. This isolates the model's own reasoning from any scaffolding built around it.

All data is open. Every run publishes its full scorecard, raw model responses, judge verdicts, and drift alerts in HTML, JSON, Markdown, and plain text. The source code, prompts, and evaluation methodology are public on GitHub. If you want to verify a result or run your own analysis, everything you need is here.
