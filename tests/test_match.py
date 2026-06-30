import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from sim.Team import Team
from sim.Match import expectedScore, simulateMustWin, simulatePossibleDraw

argentina = Team("AR", "Argentina", 2148)
panama = Team("PA", "Panama", 1700)
france = Team("FR", "France", 2005)
brazil = Team("BR", "Brazil", 2031)

#Tests for Team.py and Match.py
def test_equal_ratings_returns_half():
    assert expectedScore(2000, 2000) == 0.5

def test_probabilities_sum_to_one():
    a = expectedScore(2148, 1700)
    b = expectedScore(1700, 2148)
    assert abs(a + b - 1.0) < 0.0001

def test_higher_rated_team_is_favoured():
    assert expectedScore(2148, 1700) > 0.5

def test_must_win_never_returns_none():
    for _ in range(1000):
        result = simulateMustWin(argentina, panama)
        assert result is not None
        assert result in [argentina, panama]

def test_must_win_favours_stronger_team():
    wins = sum(1 for _ in range(1000) if simulateMustWin(argentina, panama) == argentina)
    assert wins > 700  #argentina should win well over 70% vs panama

def test_possible_draw_can_return_none():
    results = [simulatePossibleDraw(france, brazil) for _ in range(1000)]
    assert None in results

def test_close_teams_draw_more_than_mismatched():
    draws_close = sum(1 for _ in range(1000) if simulatePossibleDraw(france, brazil) is None)
    draws_mismatch = sum(1 for _ in range(1000) if simulatePossibleDraw(argentina, panama) is None)
    assert draws_close > draws_mismatch