"""
fetch_rankings.py

Gathers live Elo ratings from eloratings.net and 
filters down to only the teams selected in data/teams.json
Writes results to data/rankings.json.
"""

import json
import requests
import sys
from datafc import eloratings

URL = "https://www.eloratings.net/World.tsv"

def fetchTSV():
    """
    Fetches World.tsv from eloratings.net. This file stores
    all the data about the teams.
    """

    response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    response.raise_for_status()
    rows = []

    for line in response.text.strip().split("\n"):
        cols = line.split("\t")
        if len(cols) < 4:
            continue
        rows.append(cols)
    return rows


def buildCodeMap(rows):
    """
    Builds code name map directly from World.tsv so only
    actively ranked teams are considered valid.
    Enriches with full names from the eloratings reference table.
    """
    live_codes = {cols[2] for cols in rows}

    df = eloratings.country_codes_data()
    name_lookup = dict(zip(df["country_code"], df["country_name"]))

    code_map = {
        code: name_lookup.get(code, code)
        for code in live_codes
    }

    return code_map

def loadSelectedCodes(path="data/teams.json"):

    with open(path) as f:
        data = json.load(f)
    
    if data["mode"] == "random":
        return set(data["teams"])
    else:
        return {code for codes in data["groups"].values() for code in codes}
    
def fetchRankings(selected_codes, code_map, rows):
    """
    Gets World.tsv and returns only teams whose codes
    are selected.
    """

    rankings = []
    for cols in rows:
        code = cols[2]
        if code not in selected_codes:
            continue
        rankings.append({
            "rank": int(cols[0]),
            "code": code,
            "team": code_map.get(code, code),
            "rating": int(cols[3]),
        })
    return rankings

def validateSelection(selected_codes, code_map):
    """
    Validates that exactly 48 teams were selected and
    that all codes exist in the eloratings code map.
    Aborts with a clear message if either check fails.
    """
    unknown = [code for code in selected_codes if code not in code_map]
    if unknown:
        print(f"Error: {len(unknown)} unknown team code(s): {unknown}")
        print("Check your teams.json for typos.")
        sys.exit(1)

 
    if len(selected_codes) != 48:
        print(f"Error: Expected 48 teams, got {len(selected_codes)}.")
        print("Check your teams.json and make sure exactly 48 teams are selected.")
        sys.exit(1)

if __name__ == "__main__":
    selected = loadSelectedCodes()
    code_map = buildCodeMap()
    validateSelection(selected, code_map)
    data = fetchRankings(selected,code_map)

    with open ("data/rankings.json", "w") as f:
        json.dump(data, f, indent=2)
    

