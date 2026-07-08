# World Cup Simulator

A Python-based simulator for the 2026 FIFA World Cup format. It pulls live team ratings, lets you build your own 48-team bracket (randomly or manually), and any number of tournament simulations to estimate each team's chances of winning it all.

## Features

- **Live Elo ratings** — pulls up-to-date team ratings directly from [eloratings.net](https://www.eloratings.net)
- **Two setup modes**
  - **Random** — pick 48 teams and let the simulator randomly assign groups
  - **Manual** — pick 48 teams and assign teams to all 12 groups (A–L) yourself
- **Full tournament simulation** — group stage (round robin), knockout bracket (Round of 32 through the Final), including the 8 best third-place qualifiers per the 2026 format
- **Realistic match outcomes** — win/draw probabilities derived from Elo rating differentials
- **Batch simulations** — run as many simulations as you want and see win totals/percentages for every team
- **Save & reuse setups** — your team/group selections are saved to `data/teams.json` so you can rerun simulations without re-entering everything

## How It Works

1. The simulator fetches current team ratings from eloratings.net
2. You select 48 teams, either letting the script randomize groups or assigning them yourself
3. Group stage matches are simulated using each team's Elo rating, with standings resolved by points, head-to-head results, and wins
4. The top 2 teams from each group plus the 8 best third-place teams advance to a 32-team knockout bracket
5. The bracket plays out through the Round of 32, Round of 16, Quarterfinals, Semifinals, and Final
6. Repeat as many times as you like, and see which teams win the most often

## Getting Started

### Prerequisites

- Python 3.11+

### Installation

```bash
git clone https://github.com/your-username/WorldCupSimulator.git
cd WorldCupSimulator
pip install requests
```

### Usage

Run the simulator from the project root:

```bash
python main.py
```

You'll be prompted to:
1. Choose **Random** or **Manual** group assignment
2. Select your 48 teams (type `LIST` at any prompt to see valid team codes)
3. Enter the number of simulations to run

Results are printed as a sorted table showing each team's win count and win percentage.

## Project Structure
WorldCupSimulator/
├── main.py                       
├── src/
│   ├── scraper/
│   │   └── fetchRankings.py 
│   └── sim/
│       ├── team.py          
│       ├── match.py         
│       ├── bracket.py       
│       └── tournament.py    
└── tests/
    ├── test_bracket.py 
    └── test_match.py         

## Running Tests

```bash
pip install pytest
pytest tests/
```
