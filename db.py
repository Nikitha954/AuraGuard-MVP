import sqlite3
import json
import datetime
from typing import List, Dict, Optional


DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    created_at TEXT,
    meta TEXT
);

CREATE TABLE IF NOT EXISTS video_hashes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER,
    frame_index INTEGER,
    hash TEXT,
    FOREIGN KEY(video_id) REFERENCES videos(id)
);
"""


def init_db(path: str = "video_hashes.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    cur = conn.cursor()
    for stmt in DB_SCHEMA.strip().split(";"):
        s = stmt.strip()
        if s:
            cur.execute(s)
    conn.commit()
    return conn


def insert_video_hashes(conn: sqlite3.Connection, name: str, hashes: List[str], meta: Optional[Dict] = None) -> int:
    cur = conn.cursor()
    created = datetime.datetime.utcnow().isoformat() + "Z"
    meta_json = json.dumps(meta or {})
    cur.execute("INSERT INTO videos (name, created_at, meta) VALUES (?, ?, ?)", (name, created, meta_json))
    vid = cur.lastrowid
    rows = [(vid, i, h) for i, h in enumerate(hashes)]
    cur.executemany("INSERT INTO video_hashes (video_id, frame_index, hash) VALUES (?, ?, ?)", rows)
    conn.commit()
    return vid


def list_videos(conn: sqlite3.Connection) -> List[Dict]:
    cur = conn.cursor()
    cur.execute("SELECT id, name, created_at, meta FROM videos ORDER BY created_at DESC")
    out = []
    for r in cur.fetchall():
        vid, name, created, meta = r
        try:
            meta_obj = json.loads(meta) if meta else {}
        except Exception:
            meta_obj = {}
        out.append({"id": vid, "name": name, "created_at": created, "meta": meta_obj})
    return out


def get_video_hashes(conn: sqlite3.Connection, video_id: int) -> List[str]:
    cur = conn.cursor()
    cur.execute("SELECT frame_index, hash FROM video_hashes WHERE video_id=? ORDER BY frame_index", (video_id,))
    return [r[1] for r in cur.fetchall()]


def delete_video(conn: sqlite3.Connection, video_id: int):
    cur = conn.cursor()
    cur.execute("DELETE FROM video_hashes WHERE video_id=?", (video_id,))
    cur.execute("DELETE FROM videos WHERE id=?", (video_id,))
    conn.commit()
