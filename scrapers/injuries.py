"""Official injury reports from nflverse."""
import logging

import pandas as pd

import config
from scrapers.http import get_csv

log = logging.getLogger(__name__)


def fetch_injuries():
    try:
        df = get_csv(config.INJURIES_URL)
    except Exception as exc:  # injury file can lag at the start of a season
        log.warning("Injuries unavailable: %s", exc)
        return pd.DataFrame()
    df = df.rename(columns={"gsis_id": "player_id", "full_name": "player_name"})
    df = df[["season", "week", "team", "player_id", "player_name", "position",
             "report_primary_injury", "report_status", "practice_status"]]
    log.info("Injuries: %d report rows through week %d", len(df), df["week"].max())
    return df
