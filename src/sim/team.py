"""
team.py

Defines the Team class, which contains the info
and current elo of the team. 
"""

class Team:
    def __init__(self, code, name, rating):
        self.code = code
        self.name = name
        self.rating = rating
    
    def __repr__(self):
        return f"Team({self.code}, {self.name},{self.rating})"