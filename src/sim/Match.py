"""
match.py

Simulates the outcome of a single match between two nations.
Converts the elo rating difference to a win percentage then randomly
picking a winner based on those results
"""

import random

def expectedScore(ratingA, ratingB):
    """
    Returns team A's probability of winning based on the elo
    of both teams. 0.5 means an even match and closer to 1.0 means
    team A is heavily favoured
    """
    return 1/(1+(10**(ratingB-ratingA)/400))

def simulateMatch(teamA, teamB):
    """
    Simulates a match between two teams.
    """
    chanceA = expectedScore(teamA.rating, teamB.rating)
    roll = random.random()

    if roll < chanceA:
        return teamA
    else: return teamB