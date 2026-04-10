# ABOUTME: Tests for the blind judging module.
# ABOUTME: Tests shuffle logic, response formatting, and majority vote counting.

import os

import pytest

from llm_weather.judge import (
    shuffle_responses,
    format_responses,
    majority_winner,
    judge_prompt,
)


def test_shuffle_responses_assigns_labels():
    responses = {
        "openai/gpt-4.1": {"content": "Answer A"},
        "anthropic/claude-sonnet-4-6": {"content": "Answer B"},
        "google/gemini-2.5-pro": {"content": "Answer C"},
    }
    label_to_model, label_to_content = shuffle_responses(responses)

    assert set(label_to_model.keys()) == {"A", "B", "C"}
    assert set(label_to_model.values()) == set(responses.keys())
    assert len(label_to_content) == 3
    assert all(isinstance(v, str) for v in label_to_content.values())


def test_shuffle_responses_content_matches():
    responses = {
        "model-a": {"content": "Alpha response"},
        "model-b": {"content": "Beta response"},
    }
    label_to_model, label_to_content = shuffle_responses(responses)

    for label, model in label_to_model.items():
        assert label_to_content[label] == responses[model]["content"]


def test_format_responses_includes_all_labels():
    label_to_content = {
        "A": "First answer",
        "B": "Second answer",
    }
    formatted = format_responses(label_to_content)

    assert "Response A:" in formatted
    assert "First answer" in formatted
    assert "Response B:" in formatted
    assert "Second answer" in formatted


def test_format_responses_sorted_by_label():
    label_to_content = {
        "C": "Third",
        "A": "First",
        "B": "Second",
    }
    formatted = format_responses(label_to_content)

    pos_a = formatted.index("Response A:")
    pos_b = formatted.index("Response B:")
    pos_c = formatted.index("Response C:")
    assert pos_a < pos_b < pos_c


def test_majority_winner_clear_majority():
    judge_results = {
        "judge-1": {"winner": "A", "ranking": ["A", "B", "C"], "reasoning": "..."},
        "judge-2": {"winner": "A", "ranking": ["A", "C", "B"], "reasoning": "..."},
        "judge-3": {"winner": "B", "ranking": ["B", "A", "C"], "reasoning": "..."},
    }
    assert majority_winner(judge_results) == "A"


def test_majority_winner_tie_returns_most_common():
    judge_results = {
        "judge-1": {"winner": "A", "ranking": ["A", "B"], "reasoning": "..."},
        "judge-2": {"winner": "B", "ranking": ["B", "A"], "reasoning": "..."},
        "judge-3": {"winner": "B", "ranking": ["B", "A"], "reasoning": "..."},
    }
    assert majority_winner(judge_results) == "B"


# Integration tests — require API keys
needs_api_key = pytest.mark.skipif(
    not any(os.environ.get(k) for k in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]),
    reason="No API key available",
)

TEST_JUDGE_MODEL = os.environ.get("LLM_WEATHER_TEST_MODEL", "openai/gpt-4.1-mini")


@needs_api_key
def test_judge_prompt_returns_verdict():
    label_to_content = {
        "A": "Yes, all bloops are lazzies. Since all bloops are razzies, and all razzies are lazzies, by transitivity all bloops are lazzies.",
        "B": "No, bloops are not lazzies because they are bloops.",
    }
    verdict = judge_prompt(
        "If all bloops are razzies and all razzies are lazzies, are all bloops lazzies?",
        label_to_content,
        TEST_JUDGE_MODEL,
    )
    assert "winner" in verdict
    assert verdict["winner"] in ("A", "B")
    assert "ranking" in verdict
    assert "reasoning" in verdict
