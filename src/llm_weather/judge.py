# ABOUTME: Evaluates each contestant response individually for correctness and quality.
# ABOUTME: Uses multiple judge models with majority vote on correctness, averaged scores.

import json
import logging
import re
from pathlib import Path

from litellm import completion

logger = logging.getLogger("llm_weather.judge")

EVAL_PROMPT = """Evaluate this response to a reasoning question.

Question: {question}

Response: {response}

Is the response correct? Rate the reasoning quality from 1 (poor) to 5 (excellent).

Respond in this exact JSON format and nothing else:
{{"correct": true, "score": 4, "reasoning": "one sentence explanation"}}"""


def parse_evaluation_response(text: str) -> dict:
    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if json_match:
        parsed = json.loads(json_match.group())
        parsed["correct"] = bool(parsed["correct"])
        parsed["score"] = int(parsed["score"])
        return parsed
    raise ValueError(f"Could not parse evaluation response as JSON: {text}")


def evaluate_single(question: str, response: str, judge_model: str) -> dict:
    logger.info("Judging with %s", judge_model)
    logger.debug("Question: %s", question[:100])
    logger.debug("Response being judged: %s", response[:200])
    prompt = EVAL_PROMPT.format(question=question, response=response)
    result = completion(
        model=judge_model,
        messages=[{"role": "user", "content": prompt}],
    )
    content = result.choices[0].message.content
    parsed = parse_evaluation_response(content)
    logger.info(
        "Verdict from %s: correct=%s score=%s reason=%s",
        judge_model, parsed["correct"], parsed["score"], parsed["reasoning"][:100],
    )
    return parsed


def majority_correct(verdicts: dict[str, dict]) -> bool:
    correct_count = sum(1 for v in verdicts.values() if v["correct"])
    return correct_count > len(verdicts) / 2


def average_score(verdicts: dict[str, dict]) -> float:
    scores = [v["score"] for v in verdicts.values()]
    return round(sum(scores) / len(scores), 2)


def evaluate_all(responses_data: dict, judges: list[str], run_dir: Path) -> dict:
    results = {"run_id": run_dir.name, "prompts": {}}

    for prompt_id, prompt_data in responses_data["prompts"].items():
        evaluations = {}

        for model, samples in prompt_data["responses"].items():
            # Normalize old single-response format to list
            if isinstance(samples, dict):
                samples = [samples]

            valid_samples = [s for s in samples if "error" not in s]
            if not valid_samples:
                evaluations[model] = {
                    "samples": [],
                    "judges": {},
                    "majority_correct": None,
                    "avg_score": None,
                }
                continue

            # Evaluate each sample with each judge
            all_verdicts = {}
            sample_details = []
            for i, sample in enumerate(valid_samples):
                sample_verdicts = {}
                for judge_model in judges:
                    key = f"{judge_model}:s{i}"
                    try:
                        verdict = evaluate_single(
                            prompt_data["prompt"], sample["content"], judge_model
                        )
                        all_verdicts[key] = verdict
                        sample_verdicts[judge_model] = verdict
                    except Exception as e:
                        all_verdicts[key] = {"error": str(e)}
                        sample_verdicts[judge_model] = {"error": str(e)}
                sample_details.append({"sample_index": i, "verdicts": sample_verdicts})

            valid_verdicts = {
                k: v for k, v in all_verdicts.items() if "error" not in v
            }
            if valid_verdicts:
                mc = majority_correct(valid_verdicts)
                avg = average_score(valid_verdicts)
                logger.info(
                    "=== %s | %s: correct=%s avg_score=%s (%d verdicts) ===",
                    prompt_id, model, mc, avg, len(valid_verdicts),
                )
                evaluations[model] = {
                    "samples": sample_details,
                    "judges": all_verdicts,
                    "majority_correct": mc,
                    "avg_score": avg,
                }
            else:
                evaluations[model] = {
                    "samples": sample_details,
                    "judges": all_verdicts,
                    "majority_correct": None,
                    "avg_score": None,
                }

        results["prompts"][prompt_id] = {
            "prompt": prompt_data["prompt"],
            "evaluations": evaluations,
        }

    with open(run_dir / "judgments.json", "w") as f:
        json.dump(results, f, indent=2)

    return results
