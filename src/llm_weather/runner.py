# ABOUTME: Sends curated reasoning prompts to all contestant models via LiteLLM.
# ABOUTME: Collects responses with metadata and writes responses.json per run.

import json
import time
from datetime import datetime, timezone
from pathlib import Path

from litellm import completion

SYSTEM_PROMPT = "Answer the following question. Think step by step."


def run_prompt(model: str, prompt: str) -> dict:
    start = time.monotonic()
    response = completion(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    elapsed_ms = int((time.monotonic() - start) * 1000)
    choice = response.choices[0]
    usage = response.usage
    return {
        "content": choice.message.content,
        "latency_ms": elapsed_ms,
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
    }


def run_all(prompts: list, contestants: list[str], run_dir: Path) -> dict:
    results = {
        "run_id": run_dir.name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompts": {},
    }

    for p in prompts:
        results["prompts"][p.id] = {
            "prompt": p.prompt,
            "category": p.category,
            "responses": {},
        }
        for model in contestants:
            try:
                results["prompts"][p.id]["responses"][model] = run_prompt(
                    model, p.prompt
                )
            except Exception as e:
                results["prompts"][p.id]["responses"][model] = {
                    "error": str(e),
                }

    with open(run_dir / "responses.json", "w") as f:
        json.dump(results, f, indent=2)

    return results
