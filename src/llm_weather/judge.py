# ABOUTME: Blindly evaluates contestant responses using multiple judge models.
# ABOUTME: Shuffles responses, assigns anonymous labels, and determines winners by majority vote.

import json
import random
import re
import string
from collections import Counter
from pathlib import Path

from litellm import completion

JUDGE_PROMPT = """Below are responses to a reasoning question. Rank them by quality of reasoning. Pick a winner and briefly explain why.

Question: {question}

{responses}

Respond in this exact JSON format and nothing else:
{{"winner": "<letter>", "ranking": ["<best>", "<next>", ...], "reasoning": "<one sentence>"}}"""


def shuffle_responses(responses: dict[str, dict]) -> tuple[dict[str, str], dict[str, str]]:
    models = list(responses.keys())
    random.shuffle(models)
    labels = list(string.ascii_uppercase[: len(models)])
    label_to_model = dict(zip(labels, models))
    label_to_content = {
        label: responses[model]["content"]
        for label, model in label_to_model.items()
    }
    return label_to_model, label_to_content


def format_responses(label_to_content: dict[str, str]) -> str:
    parts = []
    for label in sorted(label_to_content):
        parts.append(f"Response {label}:\n{label_to_content[label]}")
    return "\n\n".join(parts)


def parse_judge_response(text: str) -> dict:
    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    raise ValueError(f"Could not parse judge response as JSON: {text}")


def judge_prompt(question: str, label_to_content: dict[str, str], judge_model: str) -> dict:
    formatted = format_responses(label_to_content)
    prompt = JUDGE_PROMPT.format(question=question, responses=formatted)
    response = completion(
        model=judge_model,
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.choices[0].message.content
    return parse_judge_response(content)


def majority_winner(judge_results: dict[str, dict]) -> str:
    winners = [r["winner"] for r in judge_results.values()]
    counts = Counter(winners)
    return counts.most_common(1)[0][0]


def judge_all(responses_data: dict, judges: list[str], run_dir: Path) -> dict:
    results = {"run_id": run_dir.name, "prompts": {}}

    for prompt_id, prompt_data in responses_data["prompts"].items():
        valid_responses = {
            model: resp
            for model, resp in prompt_data["responses"].items()
            if "error" not in resp
        }
        if len(valid_responses) < 2:
            results["prompts"][prompt_id] = {
                "skipped": True,
                "reason": "fewer than 2 valid responses",
            }
            continue

        label_to_model, label_to_content = shuffle_responses(valid_responses)
        judge_verdicts = {}

        for judge_model in judges:
            try:
                verdict = judge_prompt(
                    prompt_data["prompt"], label_to_content, judge_model
                )
                judge_verdicts[judge_model] = verdict
            except Exception as e:
                judge_verdicts[judge_model] = {"error": str(e)}

        valid_verdicts = {
            k: v for k, v in judge_verdicts.items() if "error" not in v
        }
        if valid_verdicts:
            winner_label = majority_winner(valid_verdicts)
            winner_model = label_to_model[winner_label]
        else:
            winner_label = None
            winner_model = None

        results["prompts"][prompt_id] = {
            "shuffle_mapping": label_to_model,
            "judges": judge_verdicts,
            "majority_winner": winner_label,
            "majority_winner_model": winner_model,
        }

    with open(run_dir / "judgments.json", "w") as f:
        json.dump(results, f, indent=2)

    return results
