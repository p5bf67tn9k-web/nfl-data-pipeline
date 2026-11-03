"""Shared HTTP helpers with retries."""
import io
import logging
import time

import pandas as pd
import requests

log = logging.getLogger(__name__)
HEADERS = {"User-Agent": "nfl-data-pipeline/1.0"}


def get(url, params=None, retries=3, timeout=60):
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
            if resp.status_code < 400:
                return resp
            if resp.status_code < 500:
                # Report the path only, so API keys in params never reach the logs
                raise RuntimeError(f"HTTP {resp.status_code} from {url}: {resp.text[:200]}")
            log.warning("HTTP %s from %s (attempt %d)", resp.status_code, url, attempt)
        except requests.ConnectionError as exc:
            log.warning("Connection error on %s (attempt %d): %s", url, attempt, exc)
        time.sleep(2 ** attempt)
    raise RuntimeError(f"Failed to fetch {url} after {retries} attempts")


def get_csv(url):
    return pd.read_csv(io.BytesIO(get(url).content), low_memory=False)
