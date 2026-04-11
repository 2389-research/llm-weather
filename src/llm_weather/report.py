# ABOUTME: Generates scorecard and drift reports from individual correctness evaluations.
# ABOUTME: Compares against previous runs to detect correctness flips and score changes.

from pathlib import Path


def build_scorecard(judgments: dict) -> dict[str, dict]:
    scorecard = {}
    for prompt_id, prompt_data in judgments["prompts"].items():
        for model, eval_data in prompt_data.get("evaluations", {}).items():
            if model not in scorecard:
                scorecard[model] = {}
            scorecard[model][prompt_id] = {
                "correct": eval_data["majority_correct"],
                "score": eval_data["avg_score"],
            }
    return scorecard


def detect_drift(
    current: dict[str, dict], previous: dict[str, dict] | None
) -> list[dict]:
    if not previous:
        return []

    drift = []
    for model, prompts in current.items():
        if model not in previous:
            continue
        for prompt_id, entry in prompts.items():
            if prompt_id not in previous[model]:
                continue
            prev = previous[model][prompt_id]
            # Correctness flip
            if entry["correct"] != prev["correct"]:
                if prev["correct"] and not entry["correct"]:
                    drift.append({
                        "type": "REGRESSION",
                        "model": model,
                        "prompt": prompt_id,
                        "was": prev["correct"],
                        "now": entry["correct"],
                    })
                else:
                    drift.append({
                        "type": "IMPROVEMENT",
                        "model": model,
                        "prompt": prompt_id,
                        "was": prev["correct"],
                        "now": entry["correct"],
                    })
            # Score change >= 1.0 (only if correctness didn't flip)
            elif entry["score"] is not None and prev["score"] is not None:
                score_delta = entry["score"] - prev["score"]
                if score_delta <= -1.0:
                    drift.append({
                        "type": "SCORE_DROP",
                        "model": model,
                        "prompt": prompt_id,
                        "was": prev["score"],
                        "now": entry["score"],
                    })
                elif score_delta >= 1.0:
                    drift.append({
                        "type": "SCORE_RISE",
                        "model": model,
                        "prompt": prompt_id,
                        "was": prev["score"],
                        "now": entry["score"],
                    })
    return drift


def model_status(scorecard: dict[str, dict], drift: list[dict]) -> dict[str, str]:
    # Exclude models with no valid evaluations (all None scores)
    status = {}
    for model, prompts in scorecard.items():
        if any(entry.get("score") is not None for entry in prompts.values()):
            status[model] = "stable"
    for d in drift:
        model = d["model"]
        if model not in status:
            continue
        if d["type"] in ("REGRESSION", "SCORE_DROP"):
            status[model] = "down"
        elif d["type"] in ("IMPROVEMENT", "SCORE_RISE") and status[model] != "down":
            status[model] = "up"
    return status


def _short_model(model: str) -> str:
    return model.split("/")[-1] if "/" in model else model


def generate_headline(scorecard: dict[str, dict], drift: list[dict]) -> str:
    regressions = [d for d in drift if d["type"] == "REGRESSION"]
    score_drops = [d for d in drift if d["type"] == "SCORE_DROP"]
    improvements = [d for d in drift if d["type"] == "IMPROVEMENT"]
    score_rises = [d for d in drift if d["type"] == "SCORE_RISE"]

    # Failures not caused by drift (persistent incorrect answers)
    failures = []
    regression_keys = {(d["model"], d["prompt"]) for d in regressions}
    for model, prompts in scorecard.items():
        for pid, entry in prompts.items():
            if entry["correct"] is False and (model, pid) not in regression_keys:
                failures.append((model, pid))

    parts = []

    # Lead with regressions — the most actionable signal
    if regressions:
        models_broke = []
        for d in regressions:
            models_broke.append(f"{_short_model(d['model'])} lost {d['prompt']}")
        parts.append("; ".join(models_broke) + ".")

    # Score drops next
    if score_drops:
        models_dropped = []
        for d in score_drops:
            models_dropped.append(f"{_short_model(d['model'])} dropped on {d['prompt']}")
        parts.append("; ".join(models_dropped) + ".")

    # Persistent failures (not new regressions)
    if failures:
        failure_strs = [f"{_short_model(m)} failing {p}" for m, p in failures]
        parts.append("; ".join(failure_strs) + ".")

    # Improvements are good news, secondary
    if improvements:
        models_improved = []
        for d in improvements:
            models_improved.append(_short_model(d["model"]))
        parts.append(", ".join(models_improved) + " recovering.")

    if score_rises:
        models_rose = []
        for d in score_rises:
            models_rose.append(_short_model(d["model"]))
        parts.append(", ".join(models_rose) + " scores rising.")

    # If nothing notable, say so
    if not parts:
        parts.append("All models stable.")

    return " ".join(parts)


def generate_summary(
    scorecard: dict[str, dict], drift: list[dict], run_id: str
) -> str:
    lines = [f"# LLM Weather Report — {run_id}", ""]

    if drift:
        lines.append("## Drift Alerts")
        lines.append("")
        for d in drift:
            if d["type"] in ("REGRESSION", "IMPROVEMENT"):
                was = "correct" if d["was"] else "incorrect"
                now = "correct" if d["now"] else "incorrect"
                lines.append(f"- {d['model']} | {d['prompt']} | {d['type']}: {was} → {now}")
            else:
                lines.append(f"- {d['model']} | {d['prompt']} | {d['type']}: {d['was']} → {d['now']}")
        lines.append("")

    # Collect all prompt IDs in order
    prompt_ids = []
    for prompts in scorecard.values():
        for pid in prompts:
            if pid not in prompt_ids:
                prompt_ids.append(pid)

    lines.append("## Scorecard")
    lines.append("")
    header = "| Model | " + " | ".join(prompt_ids) + " |"
    separator = "|-------|" + "|".join("------" for _ in prompt_ids) + "|"
    lines.append(header)
    lines.append(separator)

    for model in sorted(scorecard):
        cells = []
        for pid in prompt_ids:
            entry = scorecard[model].get(pid)
            if entry and entry["correct"] is not None:
                mark = "✓" if entry["correct"] else "✗"
                cells.append(f"{mark} ({entry['score']})")
            else:
                cells.append("—")
        lines.append(f"| {model} | " + " | ".join(cells) + " |")

    lines.append("")
    return "\n".join(lines)


def generate_detail(judgments: dict, responses: dict) -> str:
    lines = [
        f"# LLM Weather Report — Detail — {judgments['run_id']}",
        "",
    ]

    for prompt_id, j_data in judgments["prompts"].items():
        r_data = responses["prompts"][prompt_id]
        lines.append(f"## {prompt_id}")
        lines.append("")
        lines.append(f"**Prompt:** {r_data['prompt']}")
        lines.append("")

        for model, eval_data in j_data.get("evaluations", {}).items():
            correct = eval_data.get("majority_correct")
            score = eval_data.get("avg_score")
            if correct is not None:
                mark = "✓" if correct else "✗"
                lines.append(f"### {model}: {mark} (score: {score})")
            else:
                lines.append(f"### {model}: — (no valid judgments)")
            lines.append("")

            # Judge verdicts
            for judge_model, verdict in eval_data.get("judges", {}).items():
                if "error" in verdict:
                    lines.append(f"- **{judge_model}:** Error — {verdict['error']}")
                else:
                    mark = "✓" if verdict["correct"] else "✗"
                    lines.append(
                        f"- **{judge_model}:** {mark} score={verdict['score']} — "
                        f"{verdict['reasoning']}"
                    )
            lines.append("")

        # Show raw responses
        lines.append("### Responses")
        lines.append("")
        for model, samples in r_data["responses"].items():
            # Normalize old single-response format to list
            if isinstance(samples, dict):
                samples = [samples]
            for i, resp in enumerate(samples):
                label = f"{model}" if len(samples) == 1 else f"{model} (sample {i + 1})"
                if "error" in resp:
                    lines.append(f"**{label}:** Error — {resp['error']}")
                else:
                    lines.append(f"**{label}** ({resp['latency_ms']}ms, {resp['output_tokens']} tokens):")
                    lines.append("")
                    lines.append(f"> {resp['content']}")
                lines.append("")

    return "\n".join(lines)


def write_reports(
    judgments: dict,
    responses: dict,
    scorecard: dict[str, dict],
    drift: list[dict],
    run_dir: Path,
) -> None:
    summary = generate_summary(scorecard, drift, judgments["run_id"])
    detail = generate_detail(judgments, responses)
    (run_dir / "summary.md").write_text(summary)
    (run_dir / "detail.md").write_text(detail)
