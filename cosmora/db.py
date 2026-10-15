from contextlib import closing
import sqlite3
from pathlib import Path

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS sources (
 id TEXT PRIMARY KEY, url TEXT NOT NULL, publisher TEXT, retrieved_at TEXT NOT NULL,
 content_sha256 TEXT NOT NULL, license_note TEXT, source_parent_id TEXT REFERENCES sources(id)
);
CREATE TABLE IF NOT EXISTS claims (
 id TEXT PRIMARY KEY, graph TEXT NOT NULL CHECK(graph IN ('historical','doctrine')),
 subject TEXT NOT NULL, predicate TEXT NOT NULL, object TEXT NOT NULL,
 source_id TEXT NOT NULL REFERENCES sources(id), evidence_quote TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('pending','verified','rejected','disputed')),
 reviewer TEXT, created_at TEXT NOT NULL, supersedes TEXT REFERENCES claims(id),
 fictional INTEGER NOT NULL DEFAULT 0 CHECK(fictional IN (0,1))
);
CREATE TABLE IF NOT EXISTS events (
 id TEXT PRIMARY KEY, person_id TEXT NOT NULL, event_type TEXT NOT NULL,
 date_start TEXT NOT NULL, date_end TEXT, date_precision TEXT NOT NULL,
 claim_id TEXT NOT NULL REFERENCES claims(id), fictional INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS calculation_runs (
 id TEXT PRIMARY KEY, person_id TEXT NOT NULL, event_id TEXT REFERENCES events(id),
 input_hash TEXT NOT NULL, engine TEXT NOT NULL, engine_version TEXT NOT NULL,
 settings_json TEXT NOT NULL, result_json TEXT NOT NULL,
 audited INTEGER NOT NULL DEFAULT 0 CHECK(audited IN (0,1))
);
CREATE TABLE IF NOT EXISTS hypotheses (
 id TEXT PRIMARY KEY, doctrine_claim_id TEXT NOT NULL REFERENCES claims(id),
 historical_event_id TEXT NOT NULL REFERENCES events(id),
 proposed_by TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('proposed','tested','rejected')),
 notes TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_log (
 id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL,
 action TEXT NOT NULL, entity_type TEXT NOT NULL, entity_id TEXT NOT NULL, detail TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_claim_graph_status ON claims(graph,status);
CREATE INDEX IF NOT EXISTS idx_events_person_date ON events(person_id,date_start);
"""

def connect(path):
    conn = sqlite3.connect(str(Path(path)))
    conn.execute('PRAGMA foreign_keys=ON')
    conn.row_factory = sqlite3.Row
    return conn

def initialize(path):
    with closing(connect(path)) as db, db:
        db.executescript(SCHEMA)
