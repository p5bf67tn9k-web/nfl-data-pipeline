"""Compare prop lines to recent results: averages and how often the over hit."""
import logging

import pandas as pd

import config

log = logging.getLogger(__name__)


def consensus_lines(props):
    """One row per player + market: the most common line and best prices across books."""
    over = props[props["side"] == "Over"]
    under = props[props["side"] == "Under"]
    line = over.groupby(["event_id", "name_key", "player_name", "market"])["line"] \
        .agg(lambda s: s.mode().iloc[0]).rename("line")
    best_over = over.groupby(["name_key", "market"])["price"].max().rename("best_over")
    best_under = under.groupby(["name_key", "market"])["price"].max().rename("best_under")
    books = over.groupby(["name_key", "market"])["bookmaker"].nunique().rename("books")
    out = line.reset_index()
    for s in (best_over, best_under, books):
        out = out.merge(s.reset_index(), on=["name_key", "market"], how="left")
    return out


def build_prop_report(props, stats, schedule, injuries, week):
    if props.empty:
        return pd.DataFrame()
    lines = consensus_lines(props)
    reg = stats[stats["season_type"] == "REG"].sort_values("week")
    latest_team = reg.groupby("name_key").tail(1)[["name_key", "player_id", "position", "team"]]
    lines = lines.merge(latest_team, on="name_key", how="left")

    unmatched = lines[lines["player_id"].isna()]["player_name"].unique()
    if len(unmatched):
        log.info("Props with no stat match (rookies/backups or name mismatch): %d", len(unmatched))

    rows = []
    for rec in lines.dropna(subset=["player_id"]).itertuples(index=False):
        stat_col = config.PROP_MARKETS[rec.market]
        games = reg[reg["player_id"] == rec.player_id].tail(config.HIT_RATE_GAMES)
        values = games[stat_col].fillna(0)
        season = reg[reg["player_id"] == rec.player_id][stat_col].fillna(0)
        rows.append({
            "player": rec.player_name,
            "position": rec.position,
            "team": rec.team,
            "market": rec.market.replace("player_", ""),
            "line": rec.line,
            "best_over": rec.best_over,
            "best_under": rec.best_under,
            "books": rec.books,
            f"last{config.HIT_RATE_GAMES}_avg": round(values.mean(), 1),
            "season_avg": round(season.mean(), 1),
            "hits": int((values > rec.line).sum()),
            "games": len(values),
            "edge": round(values.mean() - rec.line, 1),
        })
    report = pd.DataFrame(rows)
    if report.empty:
        return report

    report["hit_rate"] = (report["hits"] / report["games"]).round(2)
    report["hit_str"] = report["hits"].astype(str) + "/" + report["games"].astype(str)

    games = schedule[schedule["week"] == week]
    opp = pd.concat([
        games.rename(columns={"home_team": "team", "away_team": "opp"})[["team", "opp"]],
        games.rename(columns={"away_team": "team", "home_team": "opp"})[["team", "opp"]],
    ])
    report = report.merge(opp, on="team", how="left")

    if not injuries.empty:
        inj = injuries[["player_name", "team", "report_status"]].rename(
            columns={"player_name": "player", "report_status": "injury_status"})
        report = report.merge(inj, on=["player", "team"], how="left")

    report.insert(0, "week", week)
    # Rank by hits first so a 2/2 sample doesn't outrank 5/5
    return report.sort_values(["hits", "hit_rate", "edge"], ascending=False).reset_index(drop=True)
