# ABOUTME: Generates Hugo-compatible markdown content pages from run data.
# ABOUTME: Creates pages with YAML frontmatter for the Hugo static site.

from pathlib import Path

import yaml


def generate_hugo_content(
    run_id: str,
    leaderboard: list[dict],
    drift: list[dict],
) -> str:
    frontmatter = {
        "title": run_id,
        "date": run_id.split("T")[0] + "T" + run_id.split("T")[1].replace("-", ":"),
        "top_model": leaderboard[0]["model"] if leaderboard else "none",
        "leaderboard": leaderboard,
        "drift": drift,
    }

    lines = ["---"]
    lines.append(yaml.dump(frontmatter, default_flow_style=False).strip())
    lines.append("---")
    lines.append("")
    lines.append("## Leaderboard")
    lines.append("")
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


def write_hugo_page(content: str, run_id: str, site_dir: Path) -> Path:
    runs_dir = site_dir / "content" / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    page_path = runs_dir / f"{run_id}.md"
    page_path.write_text(content)
    return page_path
