"""
tournament.py

Is the full World Cup Simulation from start to finish.
"""

from sim.bracket import (
    createGroups,
    simulateGroup,
    rankGroup,
    getThirdPlace,
    simulateBracket
)

def runTournament(teams_by_code, data):

    #Step 1: Create the 12 groups
    groups = createGroups(teams_by_code,data)

    #Step 2: Simulate the groups
    rankedGroups = []

    for group in groups:
        curStandings, curh2h = simulateGroup(group)
        ranked = rankGroup(curStandings, curh2h)
        rankedGroups.append(ranked)
    
    #Step 3: Get Teams 32 that are advancing
    advancing = []
    i = 0

    for group in rankedGroups:
        advancing.append(group[0]["team"])
        advancing.append(group[1]["team"])
    advancing.extend(getThirdPlace(rankedGroups))

    #Step 4: Knockout phase
    champion, result = simulateBracket(advancing)

    return champion, result

    
