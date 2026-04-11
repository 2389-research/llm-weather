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
    status = {model: "stable" for model in scorecard}
    for d in drift:
        model = d["model"]
        if model not in status:
            continue
        if d["type"] in ("REGRESSION", "SCORE_DROP"):
            status[model] = "down"
        elif d["type"] in ("IMPROVEMENT", "SCORE_RISE") and status[model] != "down":
            status[model] = "up"
    return status


def generate_headline(scorecard: dict[str, dict], drift: list[dict]) -> str:
    models = list(scorecard.keys())
    prompt_ids = []
    for prompts in scorecard.values():
        for pid in prompts:
            if pid not in prompt_ids:
                prompt_ids.append(pid)

    # Count failures
    failures = []
    for model, prompts in scorecard.items():
        for pid, entry in prompts.items():
            if entry["correct"] is False:
                short_model = model.split("/")[-1] if "/" in model else model
                failures.append(f"{short_model} on {pid}")

    parts = [f"{len(models)} models, {len(prompt_ids)} prompts."]

    if not failures:
        parts.append("All correct.")
    else:
        parts.append(f"{len(failures)} incorrect: {', '.join(failures)}.")

    # Drift summary
    regressions = [d for d in drift if d["type"] == "REGRESSION"]
    improvements = [d for d in drift if d["type"] == "IMPROVEMENT"]
    score_changes = [d for d in drift if d["type"] in ("SCORE_DROP", "SCORE_RISE")]

    drift_parts = []
    if regressions:
        drift_parts.append(f"{len(regressions)} regression{'s' if len(regressions) > 1 else ''}")
    if improvements:
        drift_parts.append(f"{len(improvements)} improvement{'s' if len(improvements) > 1 else ''}")
    if score_changes:
        drift_parts.append(f"{len(score_changes)} score change{'s' if len(score_changes) > 1 else ''}")

    if drift_parts:
        parts.append(", ".join(drift_parts) + ".")
    elif not failures:
        parts.append("No drift.")

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
        for model, resp in r_data["responses"].items():
            if "error" in resp:
                lines.append(f"**{model}:** Error — {resp['error']}")
            else:
                lines.append(f"**{model}** ({resp['latency_ms']}ms, {resp['output_tokens']} tokens):")
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
