# ABOUTME: Generates Hugo-compatible markdown content pages from run data.
# ABOUTME: Creates pages with YAML frontmatter showing scorecard and drift alerts.

from pathlib import Path

import yaml


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
        "date": run_id.split("T")[0] + "T" + run_id.split("T")[1].replace("-", ":"),
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


def write_hugo_page(content: str, run_id: str, site_dir: Path) -> Path:
    runs_dir = site_dir / "content" / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    page_path = runs_dir / f"{run_id}.md"
    page_path.write_text(content)
    return page_path
