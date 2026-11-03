"""Save tables to SQLite and export CSVs."""
import logging
import sqlite3
from datetime import datetime, timezone

import config

log = logging.getLogger(__name__)


def save_tables(tables):
    config.DATA_DIR.mkdir(exist_ok=True)
    config.EXPORT_DIR.mkdir(exist_ok=True)
    with sqlite3.connect(config.DB_PATH) as conn:
        for name, df in tables.items():
            if df is None or df.empty:
                log.info("Skipped empty table: %s", name)
                continue
            df.to_sql(name, conn, if_exists="replace", index=False)
            df.to_csv(config.EXPORT_DIR / f"{name}.csv", index=False)
            log.info("Saved %s: %d rows", name, len(df))


def record_run(status, details, credits_left=None):
    with sqlite3.connect(config.DB_PATH) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS pipeline_runs "
            "(run_at TEXT, status TEXT, details TEXT, odds_credits_left INTEGER)"
        )
        conn.execute(
            "INSERT INTO pipeline_runs VALUES (?, ?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(timespec="seconds"), status, details, credits_left),
        )
