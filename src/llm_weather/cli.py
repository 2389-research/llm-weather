# ABOUTME: Click-based CLI entry point for the LLM Weather Report tool.
# ABOUTME: Provides run, report, and publish commands.

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

import click

from llm_weather.config import filter_available_models, load_models, load_prompts
from llm_weather.hugo import generate_hugo_content, generate_hugo_detail, write_hugo_page
from llm_weather.judge import evaluate_all
from llm_weather.report import (
    build_scorecard,
    detect_drift,
    generate_headline,
    model_status,
    write_reports,
)
from llm_weather.runner import run_all
from llm_weather.status import fetch_provider_status, status_for_frontmatter


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent


def find_previous_scorecard(runs_dir: Path, current_run_id: str) -> dict | None:
    if not runs_dir.exists():
        return None
    run_dirs = sorted(
        [d for d in runs_dir.iterdir() if d.is_dir() and d.name != current_run_id]
    )
    if not run_dirs:
        return None
    prev_dir = run_dirs[-1]
    judgments_path = prev_dir / "judgments.json"
    if not judgments_path.exists():
        return None
    with open(judgments_path) as f:
        prev_judgments = json.load(f)
    # Handle both old-format (leaderboard) and new-format (scorecard) judgments
    if "evaluations" in str(prev_judgments):
        return build_scorecard(prev_judgments)
    return None


def _copy_run_data(run_dir: Path, site_dir: Path, run_id: str) -> None:
    """Copy raw JSON and log files to Hugo static directory for serving."""
    static_run_dir = site_dir / "static" / "runs" / run_id
    static_run_dir.mkdir(parents=True, exist_ok=True)
    for filename in ["responses.json", "judgments.json", "run.log"]:
        src = run_dir / filename
        if src.exists():
            shutil.copy2(src, static_run_dir / filename)


@click.group()
@click.option(
    "--project-root",
    default=None,
    type=click.Path(exists=True),
    help="Project root directory (default: auto-detect).",
)
@click.pass_context
def main(ctx, project_root):
    """LLM Weather Report — track reasoning capability drift across models."""
    ctx.ensure_object(dict)
    ctx.obj["project_root"] = Path(project_root) if project_root else get_project_root()


@main.command()
@click.option(
    "--prompts",
    default=None,
    type=click.Path(exists=True),
    help="Path to prompts YAML file.",
)
@click.option(
    "--models",
    default=None,
    type=click.Path(exists=True),
    help="Path to models YAML file.",
)
@click.option(
    "--samples",
    default=2,
    type=int,
    help="Number of response samples per prompt per model (default: 2).",
)
@click.pass_context
def run(ctx, prompts, models, samples):
    """Execute a full run: prompt models, evaluate responses, generate reports."""
    root = ctx.obj["project_root"]
    prompts_path = Path(prompts) if prompts else root / "prompts.yaml"
    models_path = Path(models) if models else root / "models.yaml"
    prompts_config = load_prompts(prompts_path)
    models_config = load_models(models_path)

    contestants, skipped_contestants = filter_available_models(models_config.contestants)
    judges, skipped_judges = filter_available_models(models_config.judges)

    if not contestants:
        click.echo("No contestants have API keys configured. Nothing to run.")
        ctx.exit(1)
        return

    if not judges:
        click.echo("No judges have API keys configured. Nothing to run.")
        ctx.exit(1)
        return

    run_id = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    runs_dir = root / "runs"
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=True)

    # Set up debug logging to file
    log_path = run_dir / "run.log"
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    )
    root_logger = logging.getLogger("llm_weather")
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    # Also log to stderr at INFO level
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter("%(name)s %(message)s"))
    root_logger.addHandler(stream_handler)

    click.echo(f"Starting run {run_id}")
    click.echo(f"  Prompts: {len(prompts_config)}")
    click.echo(f"  Contestants: {len(contestants)}")
    click.echo(f"  Judges: {len(judges)}")
    click.echo(f"  Samples per prompt: {samples}")
    if skipped_contestants:
        click.echo(f"  Skipped (no API key): {', '.join(skipped_contestants)}")
    if skipped_judges:
        click.echo(f"  Skipped judges (no API key): {', '.join(skipped_judges)}")

    # Step 1: Run prompts
    click.echo("\nRunning prompts...")
    responses = run_all(prompts_config, contestants, run_dir, samples=samples)

    # Step 2: Evaluate each response individually
    click.echo("Evaluating responses...")
    judgments = evaluate_all(responses, judges, run_dir)

    # Step 3: Reports
    click.echo("Generating reports...")
    scorecard = build_scorecard(judgments)
    previous = find_previous_scorecard(runs_dir, run_id)
    drift = detect_drift(scorecard, previous)
    write_reports(judgments, responses, scorecard, drift, run_dir)

    # Step 4: Fetch provider status
    click.echo("Checking provider status feeds...")
    provider_status = fetch_provider_status()
    provider_incidents = status_for_frontmatter(provider_status)
    if provider_incidents:
        click.echo(f"  {len(provider_incidents)} recent incident(s) found")
    else:
        click.echo("  No recent incidents")

    # Step 5: Hugo content
    click.echo("Generating Hugo content...")
    headline = generate_headline(scorecard, drift)
    status = model_status(scorecard, drift)
    hugo_content = generate_hugo_content(
        run_id, scorecard, drift, headline, status, previous,
        provider_incidents=provider_incidents,
    )
    site_dir = root / "site"
    write_hugo_page(hugo_content, run_id, site_dir)

    # Step 6: Copy raw data and generate detail page
    _copy_run_data(run_dir, site_dir, run_id)
    detail_content = generate_hugo_detail(run_id, judgments, responses)
    detail_path = site_dir / "content" / "runs" / f"{run_id}-detail.md"
    detail_path.write_text(detail_content)

    click.echo(f"\nDone! Results in {run_dir}")


@main.command()
@click.argument("run_dir", type=click.Path(exists=True))
def report(run_dir):
    """Regenerate reports from existing run data."""
    run_dir = Path(run_dir)
    with open(run_dir / "responses.json") as f:
        responses = json.load(f)
    with open(run_dir / "judgments.json") as f:
        judgments = json.load(f)

    scorecard = build_scorecard(judgments)
    runs_dir = run_dir.parent
    previous = find_previous_scorecard(runs_dir, run_dir.name)
    drift = detect_drift(scorecard, previous)
    write_reports(judgments, responses, scorecard, drift, run_dir)
    click.echo(f"Reports regenerated in {run_dir}")


@main.command()
@click.pass_context
def publish(ctx):
    """Regenerate all Hugo content from runs/ and build the site."""
    root = ctx.obj["project_root"]
    runs_dir = root / "runs"
    site_dir = root / "site"

    if not runs_dir.exists():
        click.echo("No runs directory found.")
        return

    run_dirs = sorted([d for d in runs_dir.iterdir() if d.is_dir()])
    for run_dir in run_dirs:
        judgments_path = run_dir / "judgments.json"
        if not judgments_path.exists():
            continue

        with open(judgments_path) as f:
            judgments = json.load(f)

        responses_path = run_dir / "responses.json"
        responses = {}
        if responses_path.exists():
            with open(responses_path) as f:
                responses = json.load(f)

        scorecard = build_scorecard(judgments)
        previous = find_previous_scorecard(runs_dir, run_dir.name)
        drift = detect_drift(scorecard, previous)
        headline = generate_headline(scorecard, drift)
        status = model_status(scorecard, drift)
        hugo_content = generate_hugo_content(
            run_dir.name, scorecard, drift, headline, status, previous,
        )
        write_hugo_page(hugo_content, run_dir.name, site_dir)

        # Copy raw data and generate detail page
        _copy_run_data(run_dir, site_dir, run_dir.name)
        if responses:
            detail_content = generate_hugo_detail(run_dir.name, judgments, responses)
            detail_path = site_dir / "content" / "runs" / f"{run_dir.name}-detail.md"
            detail_path.write_text(detail_content)

    click.echo(f"Hugo content generated for {len(run_dirs)} runs in {site_dir}")
