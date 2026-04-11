# ABOUTME: Generates Hugo-compatible markdown content pages from run data.
# ABOUTME: Creates pages with YAML frontmatter showing scorecard and drift alerts.

from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml


def _run_id_to_central(run_id: str) -> str:
    """Convert a UTC run_id timestamp to Central time ISO string."""
    date_part, time_part = run_id.split("T")
    utc_str = f"{date_part}T{time_part.replace('-', ':')}"
    utc_dt = datetime.fromisoformat(utc_str).replace(tzinfo=timezone.utc)
    central = utc_dt.astimezone(ZoneInfo("America/Chicago"))
    return central.isoformat()


def generate_hugo_content(
    run_id: str,
    scorecard: dict[str, dict],
    drift: list[dict],
    headline: str = "",
    status: dict[str, str] | None = None,
    previous: dict[str, dict] | None = None,
) -> str:
    frontmatter = {
        "title": run_id,
        "date": _run_id_to_central(run_id),
        "outputs": ["HTML", "markdown", "rawjson"],
        "headline": headline,
        "status": status or {},
        "scorecard": scorecard,
        "drift": drift,
        "previous": previous or {},
    }

    lines = ["---"]
    lines.append(yaml.dump(frontmatter, default_flow_style=False).strip())
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def generate_hugo_detail(run_id: str, judgments: dict, responses: dict) -> str:
    """Generate a Hugo detail page with full eval logs per prompt × model."""
    date_str = _run_id_to_central(run_id)
    frontmatter = {
        "title": f"{run_id} — Detail",
        "date": date_str,
        "layout": "detail",
        "parent_run": run_id,
    }

    lines = ["---"]
    lines.append(yaml.dump(frontmatter, default_flow_style=False).strip())
    lines.append("---")
    lines.append("")

    for prompt_id, j_data in judgments.get("prompts", {}).items():
        r_data = responses.get("prompts", {}).get(prompt_id, {})
        lines.append(f"## {prompt_id}")
        lines.append("")
        lines.append(f"**Prompt:** {r_data.get('prompt', '(unknown)')}")
        lines.append("")

        # Show responses
        resp_data = r_data.get("responses", {})
        model_list = list(resp_data.keys())
        for mi, model in enumerate(model_list):
            samples = resp_data[model]
            if isinstance(samples, dict):
                samples = [samples]
            for i, resp in enumerate(samples):
                label = model if len(samples) == 1 else f"{model} (sample {i + 1})"
                if "error" in resp:
                    lines.append(f"**{label}:** Error — {resp['error']}")
                else:
                    lines.append(
                        f"**{label}** ({resp['latency_ms']}ms, "
                        f"{resp['output_tokens']} tokens):"
                    )
                    lines.append("")
                    lines.append("```")
                    lines.append(resp["content"])
                    lines.append("```")
                lines.append("")
            if mi < len(model_list) - 1:
                lines.append("---")
                lines.append("")

        # Show judge verdicts
        evals = j_data.get("evaluations", {})
        for model, eval_data in evals.items():
            correct = eval_data.get("majority_correct")
            score = eval_data.get("avg_score")
            mark = "✓" if correct else ("✗" if correct is False else "—")
            lines.append(f"### Verdict: {model} — {mark} (score: {score})")
            lines.append("")

            for sample_detail in eval_data.get("samples", []):
                si = sample_detail.get("sample_index", 0)
                for judge_model, verdict in sample_detail.get("verdicts", {}).items():
                    if "error" in verdict:
                        lines.append(f"- **{judge_model}** (s{si}): Error — {verdict['error']}")
                    else:
                        v_mark = "✓" if verdict["correct"] else "✗"
                        lines.append(
                            f"- **{judge_model}** (s{si}): {v_mark} "
                            f"score={verdict['score']} — {verdict['reasoning']}"
                        )
            lines.append("")

    # Links to raw data
    lines.append("## Raw Data")
    lines.append("")
    lines.append(f"- [responses.json](/runs/{run_id}/responses.json)")
    lines.append(f"- [judgments.json](/runs/{run_id}/judgments.json)")
    lines.append(f"- [run.log](/runs/{run_id}/run.log)")
    lines.append("")

    return "\n".join(lines)


def write_hugo_page(content: str, run_id: str, site_dir: Path) -> Path:
    runs_dir = site_dir / "content" / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    page_path = runs_dir / f"{run_id}.md"
    page_path.write_text(content)
    return page_path
