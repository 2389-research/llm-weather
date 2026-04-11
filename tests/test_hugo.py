# ABOUTME: Tests for Hugo content page generation from run data.
# ABOUTME: Verifies frontmatter and body content of generated markdown files.

import yaml

from llm_weather.hugo import generate_hugo_content, write_hugo_page


SAMPLE_SCORECARD = {
    "model-a": {
        "logic-1": {"correct": True, "score": 5.0},
        "math-1": {"correct": True, "score": 4.0},
    },
    "model-b": {
        "logic-1": {"correct": False, "score": 2.0},
        "math-1": {"correct": True, "score": 3.0},
    },
}

SAMPLE_DRIFT = [
    {"type": "REGRESSION", "model": "model-b", "prompt": "logic-1", "was": True, "now": False},
]


def test_generate_hugo_content_has_frontmatter():
    content = generate_hugo_content(
        run_id="2026-04-10T14-00-00",
        scorecard=SAMPLE_SCORECARD,
        drift=SAMPLE_DRIFT,
    )
    assert content.startswith("---\n")
    parts = content.split("---\n", 2)
    frontmatter = yaml.safe_load(parts[1])
    assert frontmatter["title"] == "2026-04-10T14-00-00"
    assert frontmatter["scorecard"] == SAMPLE_SCORECARD


def test_generate_hugo_content_date_is_valid_iso():
    content = generate_hugo_content(
        run_id="2026-04-10T19-11-30",
        scorecard=SAMPLE_SCORECARD,
        drift=[],
    )
    parts = content.split("---\n", 2)
    raw = parts[1]
    assert "2026-04-10T19:11:30" in raw


def test_generate_hugo_content_has_scorecard_in_frontmatter():
    content = generate_hugo_content(
        run_id="2026-04-10T14-00-00",
        scorecard=SAMPLE_SCORECARD,
        drift=[],
    )
    parts = content.split("---\n", 2)
    frontmatter = yaml.safe_load(parts[1])
    assert "model-a" in frontmatter["scorecard"]
    assert "model-b" in frontmatter["scorecard"]
    assert frontmatter["scorecard"]["model-a"]["logic-1"]["correct"] is True
    assert frontmatter["scorecard"]["model-b"]["logic-1"]["correct"] is False


def test_generate_hugo_content_has_drift_in_frontmatter():
    content = generate_hugo_content(
        run_id="2026-04-10T14-00-00",
        scorecard=SAMPLE_SCORECARD,
        drift=SAMPLE_DRIFT,
    )
    parts = content.split("---\n", 2)
    frontmatter = yaml.safe_load(parts[1])
    assert len(frontmatter["drift"]) == 1
    assert frontmatter["drift"][0]["type"] == "REGRESSION"
    assert frontmatter["drift"][0]["model"] == "model-b"


def test_write_hugo_page_creates_file(tmp_path):
    content = generate_hugo_content(
        run_id="2026-04-10T14-00-00",
        scorecard=SAMPLE_SCORECARD,
        drift=[],
    )
    site_dir = tmp_path / "site"
    write_hugo_page(content, "2026-04-10T14-00-00", site_dir)

    page_path = site_dir / "content" / "runs" / "2026-04-10T14-00-00.md"
    assert page_path.exists()
    assert "model-a" in page_path.read_text()
