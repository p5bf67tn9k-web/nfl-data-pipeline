"""Central settings for the NFL data pipeline."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

SEASON = int(os.getenv("NFL_SEASON", "2026"))
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")

DATA_DIR = ROOT / "data"
EXPORT_DIR = ROOT / "exports"
LOG_DIR = ROOT / "logs"
DB_PATH = DATA_DIR / "nfl.db"

NFLVERSE = "https://github.com/nflverse/nflverse-data/releases/download"
STATS_URL = f"{NFLVERSE}/stats_player/stats_player_week_{SEASON}.csv"
INJURIES_URL = f"{NFLVERSE}/injuries/injuries_{SEASON}.csv"
SCHEDULE_URL = "https://github.com/nflverse/nfldata/raw/master/data/games.csv"

ODDS_BASE = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl"
ODDS_REGION = "us"
BOOKMAKERS = "draftkings,fanduel,betmgm,caesars"
GAME_MARKETS = "h2h,spreads,totals"

# Odds API prop market -> nflverse stat column
PROP_MARKETS = {
    "player_pass_yds": "passing_yards",
    "player_pass_tds": "passing_tds",
    "player_rush_yds": "rushing_yards",
    "player_receptions": "receptions",
    "player_reception_yds": "receiving_yards",
}

# Each prop pull costs (markets x games) credits; skip props below this balance.
MIN_CREDITS_FOR_PROPS = 100
HIT_RATE_GAMES = 5

TEAM_ABBR = {
    "Arizona Cardinals": "ARI", "Atlanta Falcons": "ATL", "Baltimore Ravens": "BAL",
    "Buffalo Bills": "BUF", "Carolina Panthers": "CAR", "Chicago Bears": "CHI",
    "Cincinnati Bengals": "CIN", "Cleveland Browns": "CLE", "Dallas Cowboys": "DAL",
    "Denver Broncos": "DEN", "Detroit Lions": "DET", "Green Bay Packers": "GB",
    "Houston Texans": "HOU", "Indianapolis Colts": "IND", "Jacksonville Jaguars": "JAX",
    "Kansas City Chiefs": "KC", "Las Vegas Raiders": "LV", "Los Angeles Chargers": "LAC",
    "Los Angeles Rams": "LA", "Miami Dolphins": "MIA", "Minnesota Vikings": "MIN",
    "New England Patriots": "NE", "New Orleans Saints": "NO", "New York Giants": "NYG",
    "New York Jets": "NYJ", "Philadelphia Eagles": "PHI", "Pittsburgh Steelers": "PIT",
    "San Francisco 49ers": "SF", "Seattle Seahawks": "SEA", "Tampa Bay Buccaneers": "TB",
    "Tennessee Titans": "TEN", "Washington Commanders": "WAS",
}
