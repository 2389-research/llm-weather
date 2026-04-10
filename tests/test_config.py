# ABOUTME: Tests for YAML config loading and validation.
# ABOUTME: Uses real fixture files, no mocking.

from pathlib import Path

from llm_weather.config import (
    Prompt, ModelsConfig, load_prompts, load_models,
    has_api_key, filter_available_models,
)

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


def test_has_api_key_ollama_always_true():
    assert has_api_key("ollama/llama3") is True


def test_has_api_key_unknown_provider_no_key():
    assert has_api_key("fakeprovider/model") is False


def test_filter_available_models_splits_correctly(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    models = ["openai/gpt-4.1", "anthropic/claude-sonnet-4-6", "ollama/llama3"]
    available, skipped = filter_available_models(models)
    assert "openai/gpt-4.1" in available
    assert "ollama/llama3" in available
    assert "anthropic/claude-sonnet-4-6" in skipped
