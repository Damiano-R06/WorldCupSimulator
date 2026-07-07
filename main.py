"""
main.py

Entry point for the World Cup Sim. Where
the user does selections for the simulator.
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from sim.team import Team
from sim.tournament import runTournament
from scraper.fetchRankings import (
    fetchTSV,
    buildCodeMap,
    loadSelectedCodes,
    fetchRankings,
    validateSelection
)

def selectMode():
    """
    Asks the user which mode he would like:
    Random or manually assign groups.
    """

    print("\n=== World Cup Simulator == \n")
    print("How would you like to assign groups?\n")
    print("1 --> RANDOM\n2 --> MANUAL")

    while True:
        choice = input("\nEnter 1 or 2: ")

        if choice == "1":
            return "random"
        elif choice == "2":
            return "manual"
        else:
            print("Invalid input, enter 1 or 2.\n")

def selectNumberSims():
    """
    Gets the user's selection for the amount of simulations
    they want to run with the selected teams.
    """
    while True:
        try:
            choice = int(input("\nHow many simulations would you like to run? "))
            if choice > 0:
                return choice
            print("Must be a positve number. \n")
        except ValueError:
            print("Invalid input, enter a positive integer.\n")

def selectTeamsRandom(code_map):
    """
    Prompts the user to select 48 teams. Groups will
    be randomly selected.
    """

    print("\nEnter 48 team codes one at a time. (e.g. AR, BR, FR)")
    print("Enter LIST for a list of valid team names")

    selected = []

    while len(selected) < 48:
        code = input(f"[{len(selected)}/48] Enter team code: ").strip().upper()

        if code == "LIST":
            for c, name in sorted(code_map.items(), key=lambda pair: pair[1]):
                print(f"{c} -- {name}")
            continue

        if code not in code_map:
            print("Unknown team code, type LIST to see valid team codes")
            continue

        if code in selected:
            print("Team already selcted")
            continue
        selected.append(code)
    print("48/48 Selected")
    return selected

def selectManual(code_map):
    """
    Prompts the user to select teams and which groups they 
    go into.
    """

    print("\nYou will assign 4 teams to each of 12 groups (A through L).\n")
    print("Enter LIST for a list of valid team names")
    
    groups = {}
    group_names = [chr(65+i) for i in range(12)]
    all_selected = []

    for group_name in group_names:
        print(f"\n--- Group {group_name} ---")
        group_codes = []

        while len(group_codes) < 4:
            code = input(f"[{len(group_codes)}/4] Enter team code: ").strip().upper()

            if code == "LIST":
                for c, name in sorted(code_map.items(), key=lambda pair: pair[1]):
                    print(f"{c} -- {name}")
                continue

            if code not in code_map:
                print("Unknown team code, type LIST to see valid team codes")
                continue
            
            if code in all_selected:
                print("Team already selcted")
                continue

            group_codes.append(code)
            all_selected.append(code)
        
        groups[group_name] = group_codes
    
    return groups

def saveTeamsJson(mode, teams_data):
    """
    Writes the user's selection to data/teams.json.
    """
    os.makedirs("data", exist_ok=True)
    if mode == "random":
        data = {"mode": "random", "teams": teams_data}
    else:
        data = {"mode": "manual", "groups": teams_data}
    
    with open("data/teams.json", "w") as f:
        json.dump(data, f, indent=2)
    
    return data

def buildTeamsbyCode(rankings):
    """
    Converts the rankings list into a dict of code.
    """

    return {
        entry["code"]: Team(entry["code"], entry["team"], entry["rating"])
        for entry in rankings
    }

def printResults(win_counts, teams_by_code, sim_count):
    """
    Prints sorted table of winners.
    """
    print(f"\n=== Results after {sim_count} simulations ===\n")
    print(f"  {'Team':<25} {'Wins':>6} {'Win %':>8}")
    print(f"  {'-' * 41}")

    sorted_teams = sorted(
        win_counts.items(),
        key=lambda x: x[1],
        reverse = True
    )
    no_wins = []
    for code, wins in sorted_teams:
        if wins == 0:
            no_wins.append(code) 
            continue
        name = teams_by_code[code].name
        pct = (wins/sim_count)*100
        print(f"  {name:<25} {wins:>6} {pct:>7.1f}%")
    
    if no_wins:
        print(f"\n  {len(no_wins)} teams never won a simulation.")

def checkExistingTeams():
    """
    Checks if a previous teams.json exists and asks
    the user if they want to reuse it.
    Returns the existing data if yes, None if no.
    """
    if not os.path.exists("data/teams.json"):
        return None

    with open("data/teams.json") as f:
        data = json.load(f)

    if data["mode"] == "random":
        teams = data["teams"]
    else:
        teams = [code for codes in data["groups"].values() for code in codes]

    print("\nFound a previous tournament setup:")
    print(f"  Mode: {data['mode']}")
    print(f"  Teams: {', '.join(teams)} ({len(teams)} total)")
    print("\nWould you like to reuse tis setup?")
    print("  1. Yes — reuse saved log")
    print("  2. No — pick new log")

    while True:
        choice = input("\nEnter 1 or 2: ").strip()
        if choice == "1":
            return data
        elif choice == "2":
            return None
        else:
            print("Invalid input, enter 1 or 2.")


def main():

    existing = checkExistingTeams()


    if existing:
        data = existing
        mode = data["mode"]
        print("\nReusing saved teams")
    else:
        mode = selectMode()
    
    worldTSV = fetchTSV()
    code_map = buildCodeMap(worldTSV)

    if not existing:
        if mode == "random":
            teams_data = selectTeamsRandom(code_map)
        else:
            teams_data = selectManual(code_map)
        data = saveTeamsJson(mode, teams_data)

    selected = loadSelectedCodes("data/teams.json")
    validateSelection(selected, code_map)
    rankings = fetchRankings(selected, code_map, worldTSV)

    with open("data/rankings.json", "w") as f:
        json.dump(rankings, f, indent=2)
    
    teams_by_code = buildTeamsbyCode(rankings)

    sim_count = selectNumberSims()

    print(f"\n === Running {sim_count} Simulations ===\n")

    win_counts = {code: 0 for code in teams_by_code}

    for i in range(sim_count):
        print(f"Simulating... {i + 1}/{sim_count}", end="\r")
        champion, _ = runTournament(teams_by_code, data)
        win_counts[champion.code] += 1

    print(f"\nCompleted {sim_count} simulations")

    printResults(win_counts, teams_by_code, sim_count)

if __name__ == "__main__":
    main()