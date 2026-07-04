"""
bracket.py

Handles the entire bracket of the tournament covering 
both the group phase and the knockout rounds.

Per the 2026WC format:
48 teams are split into 12 groups of 4. Top 2 from each group advance,
plus the 8 best third-place teams, for a 32-team knockout stage.
"""

import random
from sim.match import simulateMustWin, simulatePossibleDraw

def createGroups(teams_by_code, data):
    """
    Creates tournament groups from teams.json

    There's random mode: shuffles all teams into 12 random 
    groups.
    Manual mode: use the user's prebuilt groups.
    """

    mode = data.get("mode", "random")

    if mode == "random":
        return randomGroups(teams_by_code, data["teams"])
    else: return manualGroups(teams_by_code, data["groups"])

def randomGroups(teams_by_code, codes):

    teams = [teams_by_code[code] for code in codes]
    random.shuffle(teams)

    return [teams[i*4 : i*4 + 4] for i in range(12)]

def manualGroups(teams_by_code, groupData):

    groups = []

    for group_name, codes in groupData.items():
        group = [teams_by_code[code] for code in codes]
        groups.append(group)
    return groups

def simulateGroup(group):
    """
    Simulates all matches in a single group.
    Each team plays eachother with the following scoring:
    0 for lose.
    1 for tie.
    3 for win.
    """
    standings ={
        team.code: {
            "team": team,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "points": 0
        }
        for team in group
    }

    h2h = {
        team.code: {other.code: 0 for other in group if other.code != team.code}
        for team in group
    }

    for i in range(len(group)):
        for j in range(i+1, len(group)):
            teamA = group[i]
            teamB = group[j]

            winner = simulatePossibleDraw(teamA,teamB)

            if winner is None:
                standings[teamA.code]["draws"] += 1
                standings[teamA.code]["points"] += 1
                standings[teamB.code]["draws"] += 1
                standings[teamB.code]["points"] += 1
                h2h[teamA.code][teamB.code] += 1
                h2h[teamB.code][teamA.code] += 1
            elif winner == teamA:
                standings[teamA.code]["wins"] += 1
                standings[teamA.code]["points"] += 3
                standings[teamB.code]["losses"] += 1
                h2h[teamA.code][teamB.code] += 3
            else:
                standings[teamB.code]["wins"] += 1
                standings[teamB.code]["points"] += 3
                standings[teamA.code]["losses"] += 1
                h2h[teamB.code][teamA.code] += 3
    
    return list(standings.values()), h2h

def rankGroup(standings, h2h):
    """
    Sorts a group's standings by:
    1. Points 
    2. Head-to-head
    3. Wins
    4. Random
    """

    def h2hPointsAmong(entry, tied_codes):
        """
        Returns points this team earned against the other 
        tied teams only -- not their full points totals.
        """

        code = entry["team"].code
        return sum(h2h[code][other] for other in tied_codes if other != code)
    
    by_points = sorted(standings, key=lambda entry: (entry["points"]), reverse=True)
    result = []
    i = 0

    while i < len(by_points):
        current_points = by_points[i]["points"]

        tiedTeams = []
        while i < len(by_points) and by_points[i]["points"] == current_points:
            tiedTeams.append(by_points[i])
            i+=1
        
        if len(tiedTeams) == 1: result.extend(tiedTeams)

        else:
            tied_codes = [entry["team"].code for entry in tiedTeams]
            tied_sorted = sorted(
                tiedTeams,
                key=lambda entry: (
                    h2hPointsAmong(entry, tied_codes),
                    entry["wins"],
                    random.random()
                ),
                reverse=True
            )
            result.extend(tied_sorted)
    return result

def getThirdPlace(ranked_groups):
    """
    Collects third place teams from each of the 
    12 groups and returns the best 8.

    ranked_groups -- list of 12 ranked standings lists, 
    output of rank_group() for each group
    """
    third_place_teams = []

    for group in ranked_groups:
        third = group[2]
        third_place_teams.append(third)
    
    sorted_thirds = sorted(
        third_place_teams,
        key=lambda entry: (
            entry["points"],
            entry["wins"],
            random.random()
        ),
        reverse=True
    )
    
    return [entry["team"] for entry in sorted_thirds[:8]]

def simulateKnockOutRound(teams, round_name):
    """
    Simulates a single round of the knock out phase of
    the tournament. 
    Returns a list of winners and a list of result dicts for display.
    """

    winners = []
    results = []

    for i in range(0, len(teams), 2):
        teamA = teams[i]
        teamB = teams[i+1]
        winner = simulateMustWin(teamA, teamB)
        if winner == teamA:
            loser = teamB
        else: loser = teamA

        winners.append(winner)
        results.append({
            "round": round_name,
            "teamA": teamA,
            "teamB": teamB,
            "winner": winner,
            "loser": loser,
        })
    return winners, results

def simulateBracket(teams):
    """
    Simulates the full knockout stage. 
    Returns champion and full match history. 
    """

    all_results = []
    rounds = [
        "RO32",
        "RO16",
        "QF",
        "SF",
        "FINAL"
    ]

    for round_name in rounds:
        teams, results = simulateKnockOutRound(teams, round_name)
        all_results.extend(results)
        print(f"\n--- {round_name} ---")
        for r in results:
            print(f"  {r['winner'].name} def. {r['loser'].name}")

    champion = teams[0]
    print(f"\n🏆 Champion: {champion.name}")
    return champion, all_results
