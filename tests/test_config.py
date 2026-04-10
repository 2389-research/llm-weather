# ABOUTME: Tests for YAML config loading and validation.
# ABOUTME: Uses real fixture files, no mocking.

from pathlib import Path

from llm_weather.config import Prompt, ModelsConfig, load_prompts, load_models

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_prompts_returns_list_of_prompts():
    prompts = load_prompts(FIXTURES / "prompts.yaml")
    assert len(prompts) == 2
    assert all(isinstance(p, Prompt) for p in prompts)


def test_load_prompts_fields():
    prompts = load_prompts(FIXTURES / "prompts.yaml")
    first = prompts[0]
    assert first.id == "test-logic"
    assert first.category == "logic"
    assert "greater than" in first.prompt


def test_load_models_returns_config():
    config = load_models(FIXTURES / "models.yaml")
    assert isinstance(config, ModelsConfig)


def test_load_models_contestants():
    config = load_models(FIXTURES / "models.yaml")
    assert config.contestants == ["openai/gpt-4.1", "anthropic/claude-sonnet-4-6"]


def test_load_models_judges():
    config = load_models(FIXTURES / "models.yaml")
    assert config.judges == ["openai/gpt-4.1"]
