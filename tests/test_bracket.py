"""
test_bracket.py

Tests for bracket.py — covers group creation, group simulation,
ranking, third place qualification, and knockout rounds.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import pytest


from sim.team import Team
from sim.bracket import (
    createGroups,
    simulateGroup,
    rankGroup,
    getThirdPlace,
    simulateKnockOutRound,
    simulateBracket,
)


#Helpers

def make_team(code, rating=1800):
    """Creates a Team with a given code and optional rating."""
    return Team(code, code, rating)


def make_48_teams():
    """Creates 48 unique dummy teams."""
    codes = [f"T{i:02d}" for i in range(48)]  # T00, T01, ... T47
    return {code: make_team(code) for code in codes}


def make_32_teams():
    """Creates 32 unique dummy teams for knockout stage."""
    codes = [f"T{i:02d}" for i in range(32)]
    return [make_team(code) for code in codes]


def make_group(ratings=(2000, 1800, 1600, 1400)):
    """Creates a group of 4 teams with given ratings."""
    return [
        Team(f"T{i}", f"Team{i}", rating)
        for i, rating in enumerate(ratings)
    ]


def make_ranked_groups():
    ranked_groups = []
    for g in range(12):
        group_standings = [
            {"team": make_team(f"G{g}P{p}"), "points": 9 - (p * 3), "wins": 3 - p}
            for p in range(4)
        ]
        ranked_groups.append(group_standings)
    return ranked_groups


#createGroups

def test_random_groups_creates_12_groups():
    teams = make_48_teams()
    data = {"mode": "random", "teams": list(teams.keys())}
    groups = createGroups(teams, data)
    assert len(groups) == 12


def test_random_groups_each_group_has_4_teams():
    teams = make_48_teams()
    data = {"mode": "random", "teams": list(teams.keys())}
    groups = createGroups(teams, data)
    for group in groups:
        assert len(group) == 4


def test_random_groups_no_duplicate_teams():
    teams = make_48_teams()
    data = {"mode": "random", "teams": list(teams.keys())}
    groups = createGroups(teams, data)
    all_codes = [team.code for group in groups for team in group]
    assert len(all_codes) == len(set(all_codes))


def test_random_groups_contains_all_teams():
    teams = make_48_teams()
    data = {"mode": "random", "teams": list(teams.keys())}
    groups = createGroups(teams, data)
    all_codes = {team.code for group in groups for team in group}
    assert all_codes == set(teams.keys())


def test_manual_groups_creates_correct_groups():
    teams = make_48_teams()
    codes = list(teams.keys())
    group_data = {
        f"Group{chr(65 + i)}": codes[i * 4 : i * 4 + 4]
        for i in range(12)
    }
    data = {"mode": "manual", "groups": group_data}
    groups = createGroups(teams, data)
    assert len(groups) == 12
    for group in groups:
        assert len(group) == 4


def test_manual_groups_teams_match_input():
    teams = make_48_teams()
    codes = list(teams.keys())
    group_data = {
        f"Group{chr(65 + i)}": codes[i * 4 : i * 4 + 4]
        for i in range(12)
    }
    data = {"mode": "manual", "groups": group_data}
    groups = createGroups(teams, data)
    all_codes = {team.code for group in groups for team in group}
    assert all_codes == set(codes)


#simulateGroup
def test_simulate_group_returns_4_standings():
    group = make_group()
    standings, h2h = simulateGroup(group)
    assert len(standings) == 4


def test_simulate_group_each_team_plays_3_games():
    group = make_group()
    standings, h2h = simulateGroup(group)
    for entry in standings:
        total_games = entry["wins"] + entry["draws"] + entry["losses"]
        assert total_games == 3


def test_simulate_group_total_points_correct():
    group = make_group()
    standings, h2h = simulateGroup(group)
    total_points = sum(entry["points"] for entry in standings)
    assert 12 <= total_points <= 24


def test_simulate_group_h2h_has_all_teams():
    group = make_group()
    standings, h2h = simulateGroup(group)
    codes = {team.code for team in group}
    assert set(h2h.keys()) == codes


def test_simulate_group_h2h_points_are_valid():
    group = make_group()
    standings, h2h = simulateGroup(group)
    for code, opponents in h2h.items():
        for opponent_code, points in opponents.items():
            assert points in [0, 1, 3]


#rankGroup

def test_rank_group_returns_4_entries():
    group = make_group()
    standings, h2h = simulateGroup(group)
    ranked = rankGroup(standings, h2h)
    assert len(ranked) == 4


def test_rank_group_sorted_by_points_descending():
    group = make_group()
    standings, h2h = simulateGroup(group)
    ranked = rankGroup(standings, h2h)
    points = [entry["points"] for entry in ranked]
    assert points == sorted(points, reverse=True)


def test_rank_group_first_place_has_most_points():
    group = make_group()
    standings, h2h = simulateGroup(group)
    ranked = rankGroup(standings, h2h)
    assert ranked[0]["points"] >= ranked[1]["points"]
    assert ranked[1]["points"] >= ranked[2]["points"]
    assert ranked[2]["points"] >= ranked[3]["points"]


#getThirdPlace

def test_get_third_place_returns_8_teams():
    ranked_groups = make_ranked_groups()
    qualifiers = getThirdPlace(ranked_groups)
    assert len(qualifiers) == 8


def test_get_third_place_returns_team_objects():
    ranked_groups = make_ranked_groups()
    qualifiers = getThirdPlace(ranked_groups)
    for team in qualifiers:
        assert isinstance(team, Team)


def test_get_third_place_no_duplicates():
    ranked_groups = make_ranked_groups()
    qualifiers = getThirdPlace(ranked_groups)
    codes = [team.code for team in qualifiers]
    assert len(codes) == len(set(codes))


#Simulate KnockOutRound

def test_knockout_round_halves_teams():
    teams = make_32_teams()
    winners, results = simulateKnockOutRound(teams, "RO32")
    assert len(winners) == 16


def test_knockout_round_correct_number_of_results():
    teams = make_32_teams()
    winners, results = simulateKnockOutRound(teams, "RO32")
    assert len(results) == 16


def test_knockout_round_winner_is_always_a_team():
    teams = make_32_teams()
    winners, results = simulateKnockOutRound(teams, "RO32")
    for result in results:
        assert result["winner"] in [result["teamA"], result["teamB"]]


def test_knockout_round_no_draws():
    teams = make_32_teams()
    winners, results = simulateKnockOutRound(teams, "RO32")
    for winner in winners:
        assert winner is not None


def test_knockout_round_loser_is_not_winner():
    teams = make_32_teams()
    winners, results = simulateKnockOutRound(teams, "RO32")
    for result in results:
        assert result["winner"] != result["loser"]


def test_knockout_round_result_has_correct_keys():
    teams = make_32_teams()
    winners, results = simulateKnockOutRound(teams, "RO32")
    for result in results:
        assert set(result.keys()) == {"round", "teamA", "teamB", "winner", "loser"}


#Simulate Bracket
def test_simulate_bracket_returns_one_champion():
    teams = make_32_teams()
    champion, all_results = simulateBracket(teams)
    assert isinstance(champion, Team)


def test_simulate_bracket_correct_total_matches():
    teams = make_32_teams()
    champion, all_results = simulateBracket(teams)
    assert len(all_results) == 31


def test_simulate_bracket_champion_is_from_original_teams():
    teams = make_32_teams()
    champion, all_results = simulateBracket(teams)
    assert champion in teams


def test_simulate_bracket_all_rounds_represented():
    teams = make_32_teams()
    champion, all_results = simulateBracket(teams)
    rounds_played = {r["round"] for r in all_results}
    assert rounds_played == {"RO32", "RO16", "QF", "SF", "FINAL"}