# ABOUTME: Evaluates each contestant response individually for correctness and quality.
# ABOUTME: Uses multiple judge models with majority vote on correctness, averaged scores.

import json
import re
from pathlib import Path

from litellm import completion

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
    prompt = EVAL_PROMPT.format(question=question, response=response)
    result = completion(
        model=judge_model,
        messages=[{"role": "user", "content": prompt}],
    )
    content = result.choices[0].message.content
    return parse_evaluation_response(content)


def majority_correct(verdicts: dict[str, dict]) -> bool:
    correct_count = sum(1 for v in verdicts.values() if v["correct"])
    return correct_count > len(verdicts) / 2


def average_score(verdicts: dict[str, dict]) -> float:
    scores = [v["score"] for v in verdicts.values()]
    return round(sum(scores) / len(scores), 2)


def evaluate_all(responses_data: dict, judges: list[str], run_dir: Path) -> dict:
    results = {"run_id": run_dir.name, "prompts": {}}

    for prompt_id, prompt_data in responses_data["prompts"].items():
        valid_responses = {
            model: resp
            for model, resp in prompt_data["responses"].items()
            if "error" not in resp
        }
        if not valid_responses:
            results["prompts"][prompt_id] = {
                "prompt": prompt_data["prompt"],
                "evaluations": {},
            }
            continue

        evaluations = {}
        for model, resp in valid_responses.items():
            judge_verdicts = {}
            for judge_model in judges:
                try:
                    verdict = evaluate_single(
                        prompt_data["prompt"], resp["content"], judge_model
                    )
                    judge_verdicts[judge_model] = verdict
                except Exception as e:
                    judge_verdicts[judge_model] = {"error": str(e)}

            valid_verdicts = {
                k: v for k, v in judge_verdicts.items() if "error" not in v
            }
            if valid_verdicts:
                evaluations[model] = {
                    "judges": judge_verdicts,
                    "majority_correct": majority_correct(valid_verdicts),
                    "avg_score": average_score(valid_verdicts),
                }
            else:
                evaluations[model] = {
                    "judges": judge_verdicts,
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
