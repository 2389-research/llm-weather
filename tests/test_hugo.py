# ABOUTME: Tests for Hugo content page generation from run data.
# ABOUTME: Verifies frontmatter and body content of generated markdown files.

import yaml

from llm_weather.hugo import generate_hugo_content, write_hugo_page


SAMPLE_LEADERBOARD = [
    {"rank": 1, "model": "model-a", "wins": 3, "total": 5},
    {"rank": 2, "model": "model-b", "wins": 2, "total": 5},
]

SAMPLE_DRIFT = [
    {"model": "model-b", "direction": "↓", "change": 1, "was": 1, "now": 2},
]


def test_generate_hugo_content_has_frontmatter():
    content = generate_hugo_content(
        run_id="2026-04-10T14-00-00",
        leaderboard=SAMPLE_LEADERBOARD,
        drift=SAMPLE_DRIFT,
    )
    assert content.startswith("---\n")
    parts = content.split("---\n", 2)
    frontmatter = yaml.safe_load(parts[1])
    assert frontmatter["title"] == "2026-04-10T14-00-00"
    assert frontmatter["top_model"] == "model-a"


def test_generate_hugo_content_has_leaderboard_in_body():
    content = generate_hugo_content(
        run_id="2026-04-10T14-00-00",
        leaderboard=SAMPLE_LEADERBOARD,
        drift=[],
    )
    assert "model-a" in content
    assert "3/5" in content


def test_generate_hugo_content_has_drift():
    content = generate_hugo_content(
        run_id="2026-04-10T14-00-00",
        leaderboard=SAMPLE_LEADERBOARD,
        drift=SAMPLE_DRIFT,
    )
    assert "↓" in content
    assert "model-b" in content


def test_write_hugo_page_creates_file(tmp_path):
    content = generate_hugo_content(
        run_id="2026-04-10T14-00-00",
        leaderboard=SAMPLE_LEADERBOARD,
        drift=[],
    )
    site_dir = tmp_path / "site"
    write_hugo_page(content, "2026-04-10T14-00-00", site_dir)

    page_path = site_dir / "content" / "runs" / "2026-04-10T14-00-00.md"
    assert page_path.exists()
    assert "model-a" in page_path.read_text()
