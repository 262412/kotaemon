from benchmark.metrics import anls_score, exact_match_score, token_f1_score


def test_exact_match_ignores_case_and_punctuation():
    assert exact_match_score("Revenue.", ["revenue"]) == 1.0


def test_token_f1_prefers_best_gold_answer():
    score = token_f1_score("net income was 10", ["income was 10", "other"])
    assert round(score, 4) == 0.8571


def test_anls_rewards_small_edit_distance():
    score = anls_score("internvl2", ["internvl"])
    assert score > 0.5
