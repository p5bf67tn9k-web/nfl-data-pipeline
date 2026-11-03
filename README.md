# NFL Data Pipeline: Stats, Odds & Props, Updated Daily

An automated pipeline that collects NFL data from 4 sources, cleans and combines it, and grades every
player prop against recent performance. It runs on a schedule with no manual work.

## What it does

| Step | Details |
|---|---|
| **Collect** | Weekly player stats, schedule & results, injury reports ([nflverse](https://github.com/nflverse)), game lines and player props ([The Odds API](https://the-odds-api.com)) |
| **Clean** | Standardizes player names (suffixes, punctuation), team codes, and dates so sources join reliably |
| **Combine** | Matches each prop to the player's stats, opponent, and injury status |
| **Grade** | Consensus line across sportsbooks, best available price, last-5 and season averages, hit rate, edge |
| **Store** | SQLite database (`data/nfl.db`) and CSV exports (`exports/`) |
| **Automate** | GitHub Actions runs daily; player props are pulled on Sundays to stay inside the free API tier |
| **Monitor** | Every run is logged to `logs/pipeline.log` and the `pipeline_runs` table, including API credits left |

## Sample output (`exports/prop_report.csv`)

| player | team | opp | market | line | last5_avg | hit rate | edge |
|---|---|---|---|---|---|---|---|
| Drake Maye | NE | GB | pass_tds | 1.5 | 2.8 | 5/5 | +1.3 |
| Joe Burrow | CIN | ATL | pass_yds | 268.5 | 330.8 | 4/5 | +62.3 |
| Tee Higgins | CIN | ATL | reception_yds | 71.5 | 114.4 | 4/5 | +42.9 |

## Tables

| Table | Rows (week 9, 2026) | Description |
|---|---|---|
| `player_stats` | ~8,400 | One row per player per game |
| `schedule` | 272 | Every game with scores, spread, total, venue |
| `injuries` | ~1,000 | Each player's latest injury report |
| `game_odds` | ~270 | Moneyline, spread, total by sportsbook |
| `props_raw` | varies | Every prop line and price by sportsbook |
| `prop_report` | varies | Graded props, ranked by recent hit rate |

## Project structure

```
scrapers/   stats.py, schedule.py, injuries.py, odds.py, http.py (retries)
pipeline/   clean.py, hit_rates.py, load.py
run.py      runs everything end to end
config.py   settings: season, sportsbooks, prop markets, credit budget
```

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
echo "ODDS_API_KEY=your_key_here" > .env
python run.py            # stats, schedule, injuries, game odds
python run.py --props    # also pull player props
```

API usage is protected by a budget guard: props are skipped if a pull would drop remaining
credits below `MIN_CREDITS_FOR_PROPS` in `config.py`.

## Scheduling (GitHub Actions)

`.github/workflows/pipeline.yml` runs daily and commits refreshed CSVs to `exports/`.
Add your key under **Settings → Secrets and variables → Actions** as `ODDS_API_KEY`.
Trigger it by hand from the **Actions** tab, with an option to include props.

## Tech

Python · pandas · requests · SQLite · GitHub Actions
