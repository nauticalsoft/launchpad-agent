"""Per-site status store.

SQLite by default (works anywhere, zero setup). Set DATABASE_URL to a Postgres
DSN on Railway to keep state in Postgres — the schema is identical and created
idempotently either way.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

STAGES = ["triage", "signup", "submit", "verify", "done"]

_SCHEMA = """
CREATE TABLE IF NOT EXISTS sites (
    id INTEGER PRIMARY KEY,
    platform TEXT NOT NULL,
    url TEXT NOT NULL,
    category TEXT DEFAULT '',
    cost TEXT DEFAULT '',
    stage TEXT DEFAULT 'triage',
    status TEXT DEFAULT 'pending',
    signup_method TEXT,
    captcha INTEGER,
    free_listing INTEGER,
    submit_url TEXT,
    notes TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS events (
    site_id INTEGER NOT NULL,
    ts TEXT DEFAULT CURRENT_TIMESTAMP,
    message TEXT NOT NULL,
    FOREIGN KEY(site_id) REFERENCES sites(id)
);
"""


def _connect():
    url = os.getenv("DATABASE_URL")
    if url:
        import psycopg  # Postgres path

        return psycopg.connect(url)
    Path("/opt/data").mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(os.getenv("STATE_DB", "/opt/data/launchpad.db"))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(sites: list) -> None:
    conn = _connect()
    cur = conn.cursor()
    cur.executescript(_SCHEMA)
    for s in sites:
        cur.execute(
            "INSERT OR IGNORE INTO sites (id, platform, url, category, cost) VALUES (?,?,?,?,?)",
            (s.id, s.platform, s.url, s.category, s.cost),
        )
    conn.commit()
    conn.close()


def all_sites() -> list[dict]:
    conn = _connect()
    rows = conn.execute("SELECT * FROM sites ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def set_stage(site_id: int, stage: str, **fields) -> None:
    assert stage in STAGES, f"bad stage {stage}"
    conn = _connect()
    cur = conn.cursor()
    cols = ["stage"]
    params: list = [stage]
    for k, v in fields.items():
        cols.append(k)
        params.append(v)
    cols.append("updated_at")
    params.append(__import__("datetime").datetime.now().isoformat())
    sql = f"UPDATE sites SET {', '.join(f'{c}=?' for c in cols)} WHERE id=?"
    params.append(site_id)
    cur.execute(sql, params)
    conn.commit()
    conn.close()


def log(site_id: int, message: str) -> None:
    conn = _connect()
    conn.execute("INSERT INTO events (site_id, message) VALUES (?,?)", (site_id, message))
    conn.commit()
    conn.close()
