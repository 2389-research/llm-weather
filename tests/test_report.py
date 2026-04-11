# ABOUTME: Tests for report generation (scorecard, drift detection, markdown output).
# ABOUTME: Uses constructed data structures, no API calls needed.

from llm_weather.report import (
    build_scorecard,
    detect_drift,
    generate_headline,
    generate_summary,
    generate_detail,
    model_status,
)


SAMPLE_JUDGMENTS = {
    "run_id": "2026-04-10T14-00-00",
    "prompts": {
        "logic-1": {
            "prompt": "Test logic question?",
            "evaluations": {
                "model-a": {
                    "samples": [{"sample_index": 0, "verdicts": {"judge-1": {"correct": True, "score": 5, "reasoning": "Perfect"}}}],
                    "judges": {
                        "judge-1:s0": {"correct": True, "score": 5, "reasoning": "Perfect"},
                    },
                    "majority_correct": True,
                    "avg_score": 5.0,
                },
                "model-b": {
                    "samples": [{"sample_index": 0, "verdicts": {"judge-1": {"correct": False, "score": 2, "reasoning": "Wrong"}}}],
                    "judges": {
                        "judge-1:s0": {"correct": False, "score": 2, "reasoning": "Wrong"},
                    },
                    "majority_correct": False,
                    "avg_score": 2.0,
                },
            },
        },
        "math-1": {
            "prompt": "Test math question?",
            "evaluations": {
                "model-a": {
                    "samples": [{"sample_index": 0, "verdicts": {"judge-1": {"correct": True, "score": 4, "reasoning": "Good"}}}],
                    "judges": {
                        "judge-1:s0": {"correct": True, "score": 4, "reasoning": "Good"},
                    },
                    "majority_correct": True,
                    "avg_score": 4.0,
                },
                "model-b": {
                    "samples": [{"sample_index": 0, "verdicts": {"judge-1": {"correct": True, "score": 3, "reasoning": "OK"}}}],
                    "judges": {
                        "judge-1:s0": {"correct": True, "score": 3, "reasoning": "OK"},
                    },
                    "majority_correct": True,
                    "avg_score": 3.0,
                },
            },
        },
    },
}

SAMPLE_RESPONSES = {
    "run_id": "2026-04-10T14-00-00",
    "timestamp": "2026-04-10T14:00:00Z",
    "samples": 2,
    "prompts": {
        "logic-1": {
            "prompt": "Test logic question?",
            "category": "logic",
            "responses": {
                "model-a": [
                    {"content": "Yes", "latency_ms": 100, "input_tokens": 10, "output_tokens": 5},
                    {"content": "Yes indeed", "latency_ms": 110, "input_tokens": 10, "output_tokens": 6},
                ],
                "model-b": [
                    {"content": "No", "latency_ms": 200, "input_tokens": 10, "output_tokens": 3},
                    {"content": "No way", "latency_ms": 190, "input_tokens": 10, "output_tokens": 4},
                ],
            },
        },
        "math-1": {
            "prompt": "Test math question?",
            "category": "math",
            "responses": {
                "model-a": [
                    {"content": "42", "latency_ms": 150, "input_tokens": 10, "output_tokens": 4},
                    {"content": "42!", "latency_ms": 140, "input_tokens": 10, "output_tokens": 4},
                ],
                "model-b": [
                    {"content": "5", "latency_ms": 120, "input_tokens": 10, "output_tokens": 3},
                    {"content": "Five", "latency_ms": 130, "input_tokens": 10, "output_tokens": 3},
                ],
            },
        },
    },
}


def test_build_scorecard_returns_model_prompt_grid():
    scorecard = build_scorecard(SAMPLE_JUDGMENTS)
    assert "model-a" in scorecard
    assert "model-b" in scorecard
    assert "logic-1" in scorecard["model-a"]
    assert "math-1" in scorecard["model-a"]


def test_build_scorecard_has_correct_and_score():
    scorecard = build_scorecard(SAMPLE_JUDGMENTS)
    entry = scorecard["model-a"]["logic-1"]
    assert entry["correct"] is True
    assert entry["score"] == 5.0


def test_build_scorecard_incorrect_model():
    scorecard = build_scorecard(SAMPLE_JUDGMENTS)
    entry = scorecard["model-b"]["logic-1"]
    assert entry["correct"] is False
    assert entry["score"] == 2.0


def test_detect_drift_no_previous():
    scorecard = build_scorecard(SAMPLE_JUDGMENTS)
    drift = detect_drift(scorecard, None)
    assert drift == []


def test_detect_drift_correctness_regression():
    current = {
        "model-a": {"logic-1": {"correct": False, "score": 2.0}},
    }
    previous = {
        "model-a": {"logic-1": {"correct": True, "score": 5.0}},
    }
    drift = detect_drift(current, previous)
    assert len(drift) == 1
    assert drift[0]["type"] == "REGRESSION"
    assert drift[0]["model"] == "model-a"
    assert drift[0]["prompt"] == "logic-1"


def test_detect_drift_correctness_improvement():
    current = {
        "model-a": {"logic-1": {"correct": True, "score": 4.0}},
    }
    previous = {
        "model-a": {"logic-1": {"correct": False, "score": 2.0}},
    }
    drift = detect_drift(current, previous)
    assert len(drift) == 1
    assert drift[0]["type"] == "IMPROVEMENT"


def test_detect_drift_score_drop():
    current = {
        "model-a": {"logic-1": {"correct": True, "score": 3.0}},
    }
    previous = {
        "model-a": {"logic-1": {"correct": True, "score": 5.0}},
    }
    drift = detect_drift(current, previous)
    assert len(drift) == 1
    assert drift[0]["type"] == "SCORE_DROP"
    assert drift[0]["was"] == 5.0
    assert drift[0]["now"] == 3.0


def test_detect_drift_no_change():
    current = {
        "model-a": {"logic-1": {"correct": True, "score": 5.0}},
    }
    previous = {
        "model-a": {"logic-1": {"correct": True, "score": 5.0}},
    }
    drift = detect_drift(current, previous)
    assert drift == []


def test_model_status_all_stable_no_previous():
    scorecard = build_scorecard(SAMPLE_JUDGMENTS)
    status = model_status(scorecard, [])
    assert status["model-a"] == "stable"
    assert status["model-b"] == "stable"


def test_model_status_regression_is_down():
    scorecard = build_scorecard(SAMPLE_JUDGMENTS)
    drift = [{"type": "REGRESSION", "model": "model-b", "prompt": "logic-1", "was": True, "now": False}]
    status = model_status(scorecard, drift)
    assert status["model-b"] == "down"
    assert status["model-a"] == "stable"


def test_model_status_improvement_is_up():
    scorecard = build_scorecard(SAMPLE_JUDGMENTS)
    drift = [{"type": "IMPROVEMENT", "model": "model-b", "prompt": "math-1", "was": False, "now": True}]
    status = model_status(scorecard, drift)
    assert status["model-b"] == "up"


def test_model_status_score_drop_is_down():
    scorecard = build_scorecard(SAMPLE_JUDGMENTS)
    drift = [{"type": "SCORE_DROP", "model": "model-a", "prompt": "logic-1", "was": 5.0, "now": 3.0}]
    status = model_status(scorecard, drift)
    assert status["model-a"] == "down"


def test_model_status_regression_overrides_improvement():
    scorecard = build_scorecard(SAMPLE_JUDGMENTS)
    drift = [
        {"type": "IMPROVEMENT", "model": "model-b", "prompt": "math-1", "was": False, "now": True},
        {"type": "REGRESSION", "model": "model-b", "prompt": "logic-1", "was": True, "now": False},
    ]
    status = model_status(scorecard, drift)
    assert status["model-b"] == "down"


def test_generate_headline_all_correct_no_drift():
    scorecard = {
        "model-a": {"logic-1": {"correct": True, "score": 5.0}},
        "model-b": {"logic-1": {"correct": True, "score": 4.0}},
    }
    headline = generate_headline(scorecard, [])
    # Should say everything is stable
    assert "stable" in headline.lower()
    # Should NOT mention any model by name when nothing is wrong
    assert "model-a" not in headline
    assert "model-b" not in headline


def test_generate_headline_with_failures_no_drift():
    scorecard = build_scorecard(SAMPLE_JUDGMENTS)
    headline = generate_headline(scorecard, [])
    # model-b got logic-1 wrong — headline should call it out
    assert "model-b" in headline
    assert "logic-1" in headline


def test_generate_headline_with_regression():
    scorecard = build_scorecard(SAMPLE_JUDGMENTS)
    drift = [{"type": "REGRESSION", "model": "model-b", "prompt": "logic-1", "was": True, "now": False}]
    headline = generate_headline(scorecard, drift)
    # Should name the model that regressed
    assert "model-b" in headline
    # Should indicate something broke
    assert "broke" in headline.lower() or "regressed" in headline.lower() or "lost" in headline.lower()


def test_generate_headline_with_improvements_only():
    scorecard = {
        "model-a": {"logic-1": {"correct": True, "score": 5.0}},
        "model-b": {"logic-1": {"correct": True, "score": 4.0}},
    }
    drift = [{"type": "IMPROVEMENT", "model": "model-b", "prompt": "logic-1", "was": False, "now": True}]
    headline = generate_headline(scorecard, drift)
    # Should name the model that improved
    assert "model-b" in headline


def test_generate_headline_regression_leads_over_improvement():
    scorecard = build_scorecard(SAMPLE_JUDGMENTS)
    drift = [
        {"type": "IMPROVEMENT", "model": "model-a", "prompt": "math-1", "was": False, "now": True},
        {"type": "REGRESSION", "model": "model-b", "prompt": "logic-1", "was": True, "now": False},
    ]
    headline = generate_headline(scorecard, drift)
    # Regression is the lead story
    reg_pos = headline.find("model-b")
    imp_pos = headline.find("model-a")
    assert reg_pos < imp_pos or imp_pos == -1


def test_generate_summary_contains_scorecard():
    scorecard = build_scorecard(SAMPLE_JUDGMENTS)
    summary = generate_summary(scorecard, [], "2026-04-10T14-00-00")
    assert "model-a" in summary
    assert "model-b" in summary
    assert "logic-1" in summary
    assert "✓" in summary
    assert "✗" in summary


def test_generate_summary_contains_drift():
    scorecard = build_scorecard(SAMPLE_JUDGMENTS)
    drift = [{"type": "REGRESSION", "model": "model-b", "prompt": "logic-1", "was": True, "now": False}]
    summary = generate_summary(scorecard, drift, "2026-04-10T14-00-00")
    assert "REGRESSION" in summary
    assert "model-b" in summary


def test_generate_detail_contains_evaluations():
    detail = generate_detail(SAMPLE_JUDGMENTS, SAMPLE_RESPONSES)
    assert "logic-1" in detail
    assert "math-1" in detail
    assert "model-a" in detail
    assert "model-b" in detail
