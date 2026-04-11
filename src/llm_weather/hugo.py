# ABOUTME: Generates Hugo-compatible markdown content pages from run data.
# ABOUTME: Creates pages with YAML frontmatter showing scorecard and drift alerts.

from pathlib import Path

import yaml


def generate_hugo_content(
    run_id: str,
    scorecard: dict[str, dict],
    drift: list[dict],
) -> str:
    frontmatter = {
        "title": run_id,
        "date": run_id.split("T")[0] + "T" + run_id.split("T")[1].replace("-", ":"),
        "scorecard": scorecard,
        "drift": drift,
    }

    lines = ["---"]
    lines.append(yaml.dump(frontmatter, default_flow_style=False).strip())
    lines.append("---")
    lines.append("")

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

    # Collect all prompt IDs
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


def write_hugo_page(content: str, run_id: str, site_dir: Path) -> Path:
    runs_dir = site_dir / "content" / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    page_path = runs_dir / f"{run_id}.md"
    page_path.write_text(content)
    return page_path
