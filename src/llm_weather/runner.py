# ABOUTME: Sends curated reasoning prompts to all contestant models via LiteLLM.
# ABOUTME: Collects responses with metadata and writes responses.json per run.

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from litellm import completion

logger = logging.getLogger("llm_weather.runner")

SYSTEM_PROMPT = "Answer the following question. Think step by step."


def run_prompt(model: str, prompt: str) -> dict:
    logger.info("Sending prompt to %s: %s", model, prompt[:80])
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
    content = choice.message.content
    logger.info(
        "Response from %s: %dms, %d tokens, content: %s",
        model, elapsed_ms, usage.completion_tokens, content[:200],
    )
    return {
        "content": content,
        "latency_ms": elapsed_ms,
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
    }


def run_all(
    prompts: list, contestants: list[str], run_dir: Path, samples: int = 2
) -> dict:
    results = {
        "run_id": run_dir.name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "samples": samples,
        "prompts": {},
    }

    for p in prompts:
        results["prompts"][p.id] = {
            "prompt": p.prompt,
            "category": p.category,
            "responses": {},
        }
        for model in contestants:
            model_samples = []
            for s in range(samples):
                logger.info(
                    "--- %s | %s | sample %d/%d ---", p.id, model, s + 1, samples,
                )
                try:
                    model_samples.append(run_prompt(model, p.prompt))
                except Exception as e:
                    logger.error("Error from %s on %s sample %d: %s", model, p.id, s + 1, e)
                    model_samples.append({"error": str(e)})
            results["prompts"][p.id]["responses"][model] = model_samples

    with open(run_dir / "responses.json", "w") as f:
        json.dump(results, f, indent=2)

    return results
