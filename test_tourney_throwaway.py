import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from sim.team import Team
from sim.tournament import runTournament

# 48 dummy teams with varied ratings
teams_by_code = {f"T{i:02d}": Team(f"T{i:02d}", f"Team {i:02d}", 1500 + i * 10) for i in range(48)}

# Random mode — just pass all 48 codes
data = {
    "mode": "random",
    "teams": list(teams_by_code.keys())
}

champion, all_results = runTournament(teams_by_code, data)
