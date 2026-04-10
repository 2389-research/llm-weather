# ABOUTME: Tests for report generation (leaderboard, drift, markdown output).
# ABOUTME: Uses constructed data structures, no API calls needed.

from llm_weather.report import build_leaderboard, detect_drift, generate_summary, generate_detail


SAMPLE_JUDGMENTS = {
    "run_id": "2026-04-10T14-00-00",
    "prompts": {
        "logic-1": {
            "shuffle_mapping": {"A": "model-a", "B": "model-b"},
            "judges": {
                "judge-1": {"winner": "A", "ranking": ["A", "B"], "reasoning": "Better"},
            },
            "majority_winner": "A",
            "majority_winner_model": "model-a",
        },
        "math-1": {
            "shuffle_mapping": {"A": "model-a", "B": "model-b"},
            "judges": {
                "judge-1": {"winner": "B", "ranking": ["B", "A"], "reasoning": "Correct"},
            },
            "majority_winner": "B",
            "majority_winner_model": "model-b",
        },
        "code-1": {
            "shuffle_mapping": {"A": "model-a", "B": "model-b"},
            "judges": {
                "judge-1": {"winner": "A", "ranking": ["A", "B"], "reasoning": "Clearer"},
            },
            "majority_winner": "A",
            "majority_winner_model": "model-a",
        },
    },
}

SAMPLE_RESPONSES = {
    "run_id": "2026-04-10T14-00-00",
    "timestamp": "2026-04-10T14:00:00Z",
    "prompts": {
        "logic-1": {
            "prompt": "Test logic question?",
            "category": "logic",
            "responses": {
                "model-a": {"content": "Yes", "latency_ms": 100, "input_tokens": 10, "output_tokens": 5},
                "model-b": {"content": "No", "latency_ms": 200, "input_tokens": 10, "output_tokens": 3},
            },
        },
        "math-1": {
            "prompt": "Test math question?",
            "category": "math",
            "responses": {
                "model-a": {"content": "42", "latency_ms": 150, "input_tokens": 10, "output_tokens": 4},
                "model-b": {"content": "5", "latency_ms": 120, "input_tokens": 10, "output_tokens": 3},
            },
        },
        "code-1": {
            "prompt": "Test code question?",
            "category": "code",
            "responses": {
                "model-a": {"content": "result", "latency_ms": 180, "input_tokens": 15, "output_tokens": 8},
                "model-b": {"content": "output", "latency_ms": 160, "input_tokens": 15, "output_tokens": 6},
            },
        },
    },
}


def test_build_leaderboard_ranks_by_wins():
    leaderboard = build_leaderboard(SAMPLE_JUDGMENTS)
    assert leaderboard[0]["model"] == "model-a"
    assert leaderboard[0]["wins"] == 2
    assert leaderboard[0]["rank"] == 1
    assert leaderboard[1]["model"] == "model-b"
    assert leaderboard[1]["wins"] == 1
    assert leaderboard[1]["rank"] == 2


def test_build_leaderboard_total_is_prompt_count():
    leaderboard = build_leaderboard(SAMPLE_JUDGMENTS)
    assert leaderboard[0]["total"] == 3


def test_detect_drift_no_previous():
    current = [{"model": "model-a", "rank": 1}]
    drift = detect_drift(current, None)
    assert drift == []


def test_detect_drift_detects_rank_change():
    current = [
        {"model": "model-a", "rank": 1},
        {"model": "model-b", "rank": 2},
    ]
    previous = [
        {"model": "model-a", "rank": 2},
        {"model": "model-b", "rank": 1},
    ]
    drift = detect_drift(current, previous)
    assert len(drift) == 2
    model_a_drift = next(d for d in drift if d["model"] == "model-a")
    assert model_a_drift["direction"] == "↑"
    assert model_a_drift["change"] == 1


def test_detect_drift_no_change():
    current = [{"model": "model-a", "rank": 1}]
    previous = [{"model": "model-a", "rank": 1}]
    drift = detect_drift(current, previous)
    assert drift == []


def test_generate_summary_contains_leaderboard():
    leaderboard = build_leaderboard(SAMPLE_JUDGMENTS)
    summary = generate_summary(leaderboard, [], "2026-04-10T14-00-00")
    assert "model-a" in summary
    assert "model-b" in summary
    assert "2/3" in summary
    assert "1/3" in summary


def test_generate_summary_contains_drift():
    leaderboard = build_leaderboard(SAMPLE_JUDGMENTS)
    drift = [{"model": "model-b", "direction": "↓", "change": 1, "was": 1, "now": 2}]
    summary = generate_summary(leaderboard, drift, "2026-04-10T14-00-00")
    assert "↓" in summary
    assert "model-b" in summary


def test_generate_detail_contains_prompt_breakdowns():
    detail = generate_detail(SAMPLE_JUDGMENTS, SAMPLE_RESPONSES)
    assert "logic-1" in detail
    assert "math-1" in detail
    assert "code-1" in detail
    assert "model-a" in detail
    assert "model-b" in detail
