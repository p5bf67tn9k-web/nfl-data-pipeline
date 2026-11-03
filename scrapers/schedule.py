"""Season schedule and results from nflverse."""
import logging

import config
from scrapers.http import get_csv

log = logging.getLogger(__name__)

COLUMNS = [
    "game_id", "season", "game_type", "week", "gameday", "gametime",
    "away_team", "home_team", "away_score", "home_score",
    "spread_line", "total_line", "roof", "surface", "stadium",
]


def fetch_schedule():
    df = get_csv(config.SCHEDULE_URL)
    df = df[df["season"] == config.SEASON][COLUMNS]
    log.info("Schedule: %d games in %d", len(df), config.SEASON)
    return df


def current_week(schedule):
    """First week that still has unplayed games."""
    upcoming = schedule[schedule["home_score"].isna()]
    return int(upcoming["week"].min()) if len(upcoming) else int(schedule["week"].max())
