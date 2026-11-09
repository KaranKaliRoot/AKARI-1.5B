import sqlite3
from pathlib import Path

db_path = Path("data/akari.db")
with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print("Tables:", cursor.fetchall())
    for t in ["provenance", "entries", "grammar", "vocabulary", "kanji", "readings", "senses", "examples"]:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {t};")
            print(f"Table {t} count:", cursor.fetchone()[0])
        except Exception as e:
            print(f"Table {t} error:", e)
