# ABOUTME: Tests for the runner module that sends prompts to models.
# ABOUTME: Tests the response structure from real API calls.

import os
import json

import pytest

from llm_weather.runner import run_prompt, run_all
from llm_weather.config import Prompt

# Use cheapest available model for tests
TEST_MODEL = os.environ.get("LLM_WEATHER_TEST_MODEL", "openai/gpt-4.1-mini")

needs_api_key = pytest.mark.skipif(
    not any(os.environ.get(k) for k in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]),
    reason="No API key available",
)


@needs_api_key
def test_run_prompt_returns_expected_fields():
    result = run_prompt(TEST_MODEL, "What is 1 + 1?")
    assert "content" in result
    assert "latency_ms" in result
    assert "input_tokens" in result
    assert "output_tokens" in result
    assert isinstance(result["content"], str)
    assert len(result["content"]) > 0


@needs_api_key
def test_run_prompt_latency_is_positive():
    result = run_prompt(TEST_MODEL, "Say hello.")
    assert result["latency_ms"] > 0


@needs_api_key
def test_run_all_writes_responses_json(tmp_path):
    prompts = [Prompt(id="test-1", category="math", prompt="What is 1 + 1?")]
    contestants = [TEST_MODEL]
    result = run_all(prompts, contestants, tmp_path)

    assert (tmp_path / "responses.json").exists()
    assert result["run_id"] == tmp_path.name
    assert "test-1" in result["prompts"]
    assert TEST_MODEL in result["prompts"]["test-1"]["responses"]


@needs_api_key
def test_run_all_captures_errors_without_crashing(tmp_path):
    prompts = [Prompt(id="test-1", category="math", prompt="What is 1 + 1?")]
    contestants = [TEST_MODEL, "fake-provider/nonexistent-model"]
    result = run_all(prompts, contestants, tmp_path)

    # The valid model should have a response
    assert "content" in result["prompts"]["test-1"]["responses"][TEST_MODEL]
    # The fake model should have an error recorded
    fake_resp = result["prompts"]["test-1"]["responses"]["fake-provider/nonexistent-model"]
    assert "error" in fake_resp
