"""Standardize names, teams and dates so sources join cleanly."""
import re

import pandas as pd

SUFFIXES = re.compile(r"\b(jr|sr|ii|iii|iv|v)\b")


def name_key(name):
    """'Kenneth Walker III' and 'Kenneth Walker' -> 'kenneth walker'."""
    if not isinstance(name, str):
        return None
    key = re.sub(r"[^a-z ]", "", name.lower().replace("-", " "))
    key = SUFFIXES.sub("", key)
    return " ".join(key.split())


def clean_stats(stats):
    stats = stats.copy()
    stats["name_key"] = stats["player_name"].map(name_key)
    return stats


def clean_schedule(schedule):
    schedule = schedule.copy()
    schedule["gameday"] = pd.to_datetime(schedule["gameday"]).dt.date
    return schedule


def clean_injuries(injuries):
    if injuries.empty:
        return injuries
    # Keep each player's most recent report
    latest = injuries.sort_values("week").groupby("player_id").tail(1)
    return latest.reset_index(drop=True)


def clean_props(props):
    if props.empty:
        return props
    props = props.copy()
    props["name_key"] = props["player_name"].map(name_key)
    props["commence_time"] = pd.to_datetime(props["commence_time"], utc=True)
    return props.dropna(subset=["line"])
