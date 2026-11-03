"""Run the full pipeline: collect -> clean -> combine -> save.

    python run.py            # stats, schedule, injuries, game odds
    python run.py --props    # also pull player props (~5 credits per game)
"""
import argparse
import logging
import sys

import pandas as pd

import config
from pipeline import clean, hit_rates, load
from scrapers.injuries import fetch_injuries
from scrapers.odds import OddsClient
from scrapers.schedule import current_week, fetch_schedule
from scrapers.stats import fetch_player_stats


def setup_logging():
    config.LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout),
                  logging.FileHandler(config.LOG_DIR / "pipeline.log")],
    )


def load_saved_props():
    """Reuse the last prop pull so runs without --props still refresh hit rates."""
    # CSV rather than the DB, since scheduled runs only keep the committed exports
    path = config.EXPORT_DIR / "props_raw.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def main():
    parser = argparse.ArgumentParser(description="NFL stats + odds pipeline")
    parser.add_argument("--props", action="store_true", help="pull player props (uses API credits)")
    parser.add_argument("--no-odds", action="store_true", help="skip The Odds API entirely")
    args = parser.parse_args()

    setup_logging()
    log = logging.getLogger("run")
    log.info("=== Pipeline start (season %d) ===", config.SEASON)

    odds = None
    try:
        stats = clean.clean_stats(fetch_player_stats())
        schedule = clean.clean_schedule(fetch_schedule())
        injuries = clean.clean_injuries(fetch_injuries())
        week = current_week(schedule)
        log.info("Current week: %d", week)

        game_odds, props = pd.DataFrame(), pd.DataFrame()
        if not args.no_odds:
            odds = OddsClient()
            game_odds, events = odds.game_odds()
            if args.props:
                props = clean.clean_props(odds.player_props(events))
        if props.empty:
            props = load_saved_props()
            if not props.empty:
                log.info("Using %d saved prop lines from the last props run", len(props))

        report = hit_rates.build_prop_report(props, stats, schedule, injuries, week)

        load.save_tables({
            "player_stats": stats,
            "schedule": schedule,
            "injuries": injuries,
            "game_odds": game_odds,
            "props_raw": props,
            "prop_report": report,
        })
        credits = odds.remaining if odds else None
        load.record_run("success", f"week {week}, {len(report)} props graded", credits)
        log.info("=== Done: %d props graded, odds credits left: %s ===", len(report), credits)
        if not report.empty:
            cols = ["player", "team", "opp", "market", "line", "last5_avg", "hit_str", "edge"]
            print("\nTop props by recent hit rate:\n")
            print(report[cols].head(10).to_string(index=False))
    except Exception as exc:
        log.exception("Pipeline failed")
        config.DATA_DIR.mkdir(exist_ok=True)
        load.record_run("failed", str(exc)[:500], odds.remaining if odds else None)
        sys.exit(1)


if __name__ == "__main__":
    main()
