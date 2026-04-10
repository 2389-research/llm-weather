# ABOUTME: End-to-end integration test for the full LLM Weather pipeline.
# ABOUTME: Runs one prompt through one model, judges it, and generates reports.

import json
import os

import pytest
from click.testing import CliRunner

from llm_weather.cli import main

needs_api_key = pytest.mark.skipif(
    not any(os.environ.get(k) for k in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]),
    reason="No API key available",
)

TEST_MODEL = os.environ.get("LLM_WEATHER_TEST_MODEL", "openai/gpt-4.1-mini")


@needs_api_key
def test_full_pipeline(tmp_path):
    # Create minimal config files
    prompts_file = tmp_path / "prompts.yaml"
    prompts_file.write_text(
        "prompts:\n"
        "  - id: e2e-test\n"
        "    category: math\n"
        '    prompt: "What is 2 + 2?"\n'
    )

    models_file = tmp_path / "models.yaml"
    models_file.write_text(
        f"contestants:\n"
        f"  - model: {TEST_MODEL}\n"
        f"judges:\n"
        f"  - model: {TEST_MODEL}\n"
    )

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--project-root", str(tmp_path),
            "run",
            "--prompts", str(prompts_file),
            "--models", str(models_file),
        ],
    )

    assert result.exit_code == 0, f"CLI failed: {result.output}"
    assert "Done!" in result.output

    # Verify run directory was created with expected files
    runs_dir = tmp_path / "runs"
    assert runs_dir.exists()
    run_dirs = list(runs_dir.iterdir())
    assert len(run_dirs) == 1

    run_dir = run_dirs[0]
    assert (run_dir / "responses.json").exists()
    assert (run_dir / "judgments.json").exists()
    assert (run_dir / "summary.md").exists()
    assert (run_dir / "detail.md").exists()

    # Verify Hugo content was generated
    hugo_content_dir = tmp_path / "site" / "content" / "runs"
    assert hugo_content_dir.exists()
    assert len(list(hugo_content_dir.iterdir())) == 1
