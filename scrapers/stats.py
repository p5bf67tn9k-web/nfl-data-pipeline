"""Weekly player stats from nflverse."""
import logging

import config
from scrapers.http import get_csv

log = logging.getLogger(__name__)

COLUMNS = [
    "player_id", "player_display_name", "position", "team", "opponent_team",
    "season", "week", "season_type", "game_id",
    "completions", "attempts", "passing_yards", "passing_tds", "passing_interceptions",
    "carries", "rushing_yards", "rushing_tds",
    "targets", "receptions", "receiving_yards", "receiving_tds",
    "fantasy_points_ppr",
]


def fetch_player_stats():
    df = get_csv(config.STATS_URL)
    df = df[[c for c in COLUMNS if c in df.columns]]
    df = df.rename(columns={"player_display_name": "player_name"})
    log.info("Stats: %d player-games through week %d", len(df), df["week"].max())
    return df
