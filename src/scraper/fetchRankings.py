"""
fetch_rankings.py

Gathers live Elo ratings from eloratings.net and 
filters down to only the teams selected in data/teams.json
Writes results to data/rankings.json.
"""

import json
import requests
from datafc import eloratings

URL = "https://www.eloratings.net/World.tsv"

def buildCodeMap():
    """
    Gets the offical code map from eloratings.net.
    Returns a plain dict.
    """

    df = eloratings.country_codes_data()
    return dict(zip(df["country_codes"], df["country_names"]))

def loadSelectedCodes(path="data/teams.json"):

    with open(path) as f:
        data = json.load(f)
    
    if data["mode"] == "random":
        return set(data["teams"])
    else:
        return {code for codes in data["groups"].values() for code in codes}
    
def fetchRankings(selected_codes, code_map):
    """
    Gets World.tsv and returns only teams whose codes
    are selected.
    """

    response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()

    rankings = []
    for line in response.text.strip().split("\n"):
        cols = line.split("\t")

        if len(cols) < 4:
            continue

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

