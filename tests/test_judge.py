# ABOUTME: Tests for the individual correctness evaluation module.
# ABOUTME: Tests parse logic, majority correctness, score averaging, and evaluation structure.

import os

import pytest

from llm_weather.judge import (
    parse_evaluation_response,
    majority_correct,
    average_score,
    evaluate_single,
)


def test_parse_evaluation_response_valid_json():
    text = '{"correct": true, "score": 4, "reasoning": "Good logic"}'
    result = parse_evaluation_response(text)
    assert result["correct"] is True
    assert result["score"] == 4
    assert result["reasoning"] == "Good logic"


def test_parse_evaluation_response_embedded_json():
    text = 'Here is my evaluation:\n{"correct": false, "score": 2, "reasoning": "Wrong answer"}\nThat is all.'
    result = parse_evaluation_response(text)
    assert result["correct"] is False
    assert result["score"] == 2


def test_parse_evaluation_response_invalid_raises():
    with pytest.raises(ValueError):
        parse_evaluation_response("no json here")


def test_majority_correct_all_agree_true():
    verdicts = {
        "judge-1": {"correct": True, "score": 5, "reasoning": "..."},
        "judge-2": {"correct": True, "score": 4, "reasoning": "..."},
        "judge-3": {"correct": True, "score": 5, "reasoning": "..."},
    }
    assert majority_correct(verdicts) is True


def test_majority_correct_all_agree_false():
    verdicts = {
        "judge-1": {"correct": False, "score": 1, "reasoning": "..."},
        "judge-2": {"correct": False, "score": 2, "reasoning": "..."},
    }
    assert majority_correct(verdicts) is False


def test_majority_correct_split_vote():
    verdicts = {
        "judge-1": {"correct": True, "score": 4, "reasoning": "..."},
        "judge-2": {"correct": False, "score": 2, "reasoning": "..."},
        "judge-3": {"correct": True, "score": 3, "reasoning": "..."},
    }
    assert majority_correct(verdicts) is True


def test_average_score():
    verdicts = {
        "judge-1": {"correct": True, "score": 5, "reasoning": "..."},
        "judge-2": {"correct": True, "score": 4, "reasoning": "..."},
        "judge-3": {"correct": True, "score": 3, "reasoning": "..."},
    }
    assert average_score(verdicts) == 4.0


def test_average_score_rounds_to_two_decimals():
    verdicts = {
        "judge-1": {"correct": True, "score": 5, "reasoning": "..."},
        "judge-2": {"correct": True, "score": 4, "reasoning": "..."},
        "judge-3": {"correct": True, "score": 5, "reasoning": "..."},
    }
    assert average_score(verdicts) == pytest.approx(4.67, abs=0.01)


# Integration tests — require API keys
needs_api_key = pytest.mark.skipif(
    not any(os.environ.get(k) for k in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]),
    reason="No API key available",
)

TEST_JUDGE_MODEL = os.environ.get("LLM_WEATHER_TEST_MODEL", "openai/gpt-5.4-mini")


@needs_api_key
def test_evaluate_single_returns_evaluation():
    result = evaluate_single(
        question="If all bloops are razzies and all razzies are lazzies, are all bloops lazzies?",
        response="Yes, all bloops are lazzies by transitivity.",
        judge_model=TEST_JUDGE_MODEL,
    )
    assert "correct" in result
    assert "score" in result
    assert isinstance(result["correct"], bool)
    assert 1 <= result["score"] <= 5
    assert "reasoning" in result
