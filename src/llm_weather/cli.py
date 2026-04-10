# ABOUTME: Click-based CLI entry point for the LLM Weather Report tool.
# ABOUTME: Provides run, report, and publish commands.

import json
from datetime import datetime, timezone
from pathlib import Path

import click

from llm_weather.config import filter_available_models, load_models, load_prompts
from llm_weather.hugo import generate_hugo_content, write_hugo_page
from llm_weather.judge import judge_all
from llm_weather.report import (
    build_leaderboard,
    detect_drift,
    write_reports,
)
from llm_weather.runner import run_all


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent


def find_previous_run(runs_dir: Path, current_run_id: str) -> list[dict] | None:
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
    return build_leaderboard(prev_judgments)


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
@click.pass_context
def run(ctx, prompts, models):
    """Execute a full run: prompt models, judge responses, generate reports."""
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

    click.echo(f"Starting run {run_id}")
    click.echo(f"  Prompts: {len(prompts_config)}")
    click.echo(f"  Contestants: {len(contestants)}")
    click.echo(f"  Judges: {len(judges)}")
    if skipped_contestants:
        click.echo(f"  Skipped (no API key): {', '.join(skipped_contestants)}")
    if skipped_judges:
        click.echo(f"  Skipped judges (no API key): {', '.join(skipped_judges)}")

    # Step 1: Run prompts
    click.echo("\nRunning prompts...")
    responses = run_all(prompts_config, contestants, run_dir)

    # Step 2: Judge
    click.echo("Judging responses...")
    judgments = judge_all(responses, judges, run_dir)

    # Step 3: Reports
    click.echo("Generating reports...")
    leaderboard = build_leaderboard(judgments)
    previous = find_previous_run(runs_dir, run_id)
    drift = detect_drift(leaderboard, previous)
    write_reports(judgments, responses, leaderboard, drift, run_dir)

    # Step 4: Hugo content
    click.echo("Generating Hugo content...")
    hugo_content = generate_hugo_content(run_id, leaderboard, drift)
    site_dir = root / "site"
    write_hugo_page(hugo_content, run_id, site_dir)

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

    leaderboard = build_leaderboard(judgments)
    runs_dir = run_dir.parent
    previous = find_previous_run(runs_dir, run_dir.name)
    drift = detect_drift(leaderboard, previous)
    write_reports(judgments, responses, leaderboard, drift, run_dir)
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

        leaderboard = build_leaderboard(judgments)
        previous = find_previous_run(runs_dir, run_dir.name)
        drift = detect_drift(leaderboard, previous)
        hugo_content = generate_hugo_content(run_dir.name, leaderboard, drift)
        write_hugo_page(hugo_content, run_dir.name, site_dir)

    click.echo(f"Hugo content generated for {len(run_dirs)} runs in {site_dir}")
