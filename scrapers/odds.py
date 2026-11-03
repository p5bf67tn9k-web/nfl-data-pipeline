"""Game lines and player props from The Odds API."""
import logging

import pandas as pd

import config
from scrapers.http import get

log = logging.getLogger(__name__)


class OddsClient:
    def __init__(self, api_key=config.ODDS_API_KEY):
        if not api_key:
            raise RuntimeError("ODDS_API_KEY is not set (add it to .env)")
        self.api_key = api_key
        self.remaining = None

    def _get(self, path, **params):
        resp = get(f"{config.ODDS_BASE}{path}", params={"apiKey": self.api_key, **params})
        self.remaining = int(resp.headers.get("x-requests-remaining", 0))
        return resp.json()

    def game_odds(self):
        events = self._get(
            "/odds", regions=config.ODDS_REGION, markets=config.GAME_MARKETS,
            bookmakers=config.BOOKMAKERS, oddsFormat="american",
        )
        rows = []
        for ev in events:
            for book in ev.get("bookmakers", []):
                for market in book["markets"]:
                    for out in market["outcomes"]:
                        rows.append({
                            "event_id": ev["id"],
                            "commence_time": ev["commence_time"],
                            "home_team": config.TEAM_ABBR.get(ev["home_team"], ev["home_team"]),
                            "away_team": config.TEAM_ABBR.get(ev["away_team"], ev["away_team"]),
                            "bookmaker": book["key"],
                            "market": market["key"],
                            "outcome": config.TEAM_ABBR.get(out["name"], out["name"]),
                            "price": out["price"],
                            "point": out.get("point"),
                        })
        log.info("Game odds: %d events, %d lines (credits left: %s)", len(events), len(rows), self.remaining)
        return pd.DataFrame(rows), events

    def player_props(self, events):
        markets = ",".join(config.PROP_MARKETS)
        cost = len(config.PROP_MARKETS) * len(events)
        if self.remaining is not None and self.remaining - cost < config.MIN_CREDITS_FOR_PROPS:
            log.warning("Skipping props: need ~%d credits, %d left", cost, self.remaining)
            return pd.DataFrame()
        rows = []
        for ev in events:
            data = self._get(
                f"/events/{ev['id']}/odds", regions=config.ODDS_REGION, markets=markets,
                bookmakers=config.BOOKMAKERS, oddsFormat="american",
            )
            for book in data.get("bookmakers", []):
                for market in book["markets"]:
                    for out in market["outcomes"]:
                        rows.append({
                            "event_id": ev["id"],
                            "commence_time": ev["commence_time"],
                            "bookmaker": book["key"],
                            "market": market["key"],
                            "player_name": out.get("description"),
                            "side": out["name"],
                            "line": out.get("point"),
                            "price": out["price"],
                        })
        log.info("Props: %d lines across %d games (credits left: %s)", len(rows), len(events), self.remaining)
        return pd.DataFrame(rows)
