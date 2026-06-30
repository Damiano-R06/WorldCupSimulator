"""
match.py

Simulates the outcome of a single match between two nations.
Converts the elo rating difference to a win percentage then randomly
picking a winner based on those results
"""

import random

BASE_DRAW = 0.30

def expectedScore(ratingA, ratingB):
    """
    Returns team A's probability of winning based on the elo
    of both teams. 0.5 means an even match and closer to 1.0 means
    team A is heavily favoured
    """
    return 1/(1+10**((ratingB-ratingA)/400))

def simulateMustWin(teamA, teamB):
    """
    Simulates a match between two teams, where a winner is
    always decided. Used for the knockout games.
    """
    chanceA = expectedScore(teamA.rating, teamB.rating)
    roll = random.random()

    if roll < chanceA:
        return teamA
    else: return teamB

def simulatePossibleDraw(teamA,teamB):
    """
    Simulates a match between two teams where a draw
    is possible.
    """
    chanceA = expectedScore(teamA.rating, teamB.rating)
    chanceB = 1 - chanceA

    #Closeness is higher the closer an team is at 50% chance to win
    closeness = 1 - abs(chanceA - 0.5) * 2
    chanceDraw = BASE_DRAW * closeness

    winA = chanceA * (1 - chanceDraw)

    roll = random.random()

    if roll < winA:
        return teamA
    elif roll < winA + chanceDraw:
        return None
    else: return teamB

