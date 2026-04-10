# ABOUTME: Generates summary.md (leaderboard + drift) and detail.md (per-prompt breakdowns).
# ABOUTME: Compares against previous runs to detect ranking changes.

from collections import Counter
from pathlib import Path


def build_leaderboard(judgments: dict) -> list[dict]:
    wins = Counter()
    for prompt_data in judgments["prompts"].values():
        if prompt_data.get("skipped"):
            continue
        winner = prompt_data.get("majority_winner_model")
        if winner:
            wins[winner] += 1

    total = sum(
        1 for p in judgments["prompts"].values() if not p.get("skipped")
    )
    leaderboard = []
    for rank, (model, win_count) in enumerate(wins.most_common(), 1):
        leaderboard.append(
            {"rank": rank, "model": model, "wins": win_count, "total": total}
        )
    return leaderboard


def detect_drift(
    current_leaderboard: list[dict], previous_leaderboard: list[dict] | None
) -> list[dict]:
    if not previous_leaderboard:
        return []

    prev_ranks = {entry["model"]: entry["rank"] for entry in previous_leaderboard}
    drift = []
    for entry in current_leaderboard:
        model = entry["model"]
        if model in prev_ranks:
            change = prev_ranks[model] - entry["rank"]
            if change != 0:
                drift.append(
                    {
                        "model": model,
                        "direction": "↑" if change > 0 else "↓",
                        "change": abs(change),
                        "was": prev_ranks[model],
                        "now": entry["rank"],
                    }
                )
    return drift


def generate_summary(
    leaderboard: list[dict], drift: list[dict], run_id: str
) -> str:
    lines = [f"# LLM Weather Report — {run_id}", "", "## Leaderboard", ""]
    lines.append("| Rank | Model | Wins |")
    lines.append("|------|-------|------|")
    for entry in leaderboard:
        lines.append(
            f"| {entry['rank']} | {entry['model']} | {entry['wins']}/{entry['total']} |"
        )

    if drift:
        lines.append("")
        lines.append("## Drift")
        lines.append("")
        for d in drift:
            lines.append(
                f"- {d['model']}: {d['direction']} moved {d['change']} "
                f"(was #{d['was']}, now #{d['now']})"
            )

    lines.append("")
    return "\n".join(lines)


def generate_detail(judgments: dict, responses: dict) -> str:
    lines = [
        f"# LLM Weather Report — Detail — {judgments['run_id']}",
        "",
    ]

    for prompt_id, j_data in judgments["prompts"].items():
        if j_data.get("skipped"):
            lines.append(f"## {prompt_id}")
            lines.append(f"Skipped: {j_data['reason']}")
            lines.append("")
            continue

        r_data = responses["prompts"][prompt_id]
        lines.append(f"## {prompt_id}")
        lines.append("")
        lines.append(f"**Prompt:** {r_data['prompt']}")
        lines.append("")
        lines.append(
            f"**Winner:** {j_data['majority_winner_model']} "
            f"(label {j_data['majority_winner']})"
        )
        lines.append("")

        lines.append("### Judge Verdicts")
        lines.append("")
        for judge_model, verdict in j_data["judges"].items():
            if "error" in verdict:
                lines.append(f"- **{judge_model}:** Error — {verdict['error']}")
            else:
                lines.append(
                    f"- **{judge_model}:** Winner={verdict['winner']} — "
                    f"{verdict['reasoning']}"
                )
        lines.append("")

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
    leaderboard: list[dict],
    drift: list[dict],
    run_dir: Path,
) -> None:
    summary = generate_summary(leaderboard, drift, judgments["run_id"])
    detail = generate_detail(judgments, responses)
    (run_dir / "summary.md").write_text(summary)
    (run_dir / "detail.md").write_text(detail)
