"""Verification tests for AKARI normalized database."""

import sqlite3
import sys
from pathlib import Path

# Ensure UTF-8 output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

DB_PATH = Path("data/akari_normalized.db")

def test_schema_verification():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    # 1. Schema check
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    required_tables = ['entries', 'provenance', 'readings', 'senses', 'examples', 'grammar', 'vocabulary', 'kanji']
    for table in required_tables:
        assert table in tables, f"Missing table: {table}"

    print("Schema verification passed.")

def test_version_triggers():
    conn = sqlite3.connect(DB_PATH)
    # Get a reading's entry_id
    reading = conn.execute("SELECT entry_id FROM readings LIMIT 1").fetchone()
    if not reading:
        print("No readings found to test version trigger.")
        return

    entry_id = reading[0]
    old_version = conn.execute("SELECT version FROM entries WHERE id = ?", (entry_id,)).fetchone()[0]

    # Update a reading
    conn.execute("UPDATE readings SET kana = 'new_kana' WHERE entry_id = ?", (entry_id,))
    conn.commit()

    # Verify version increment
    new_version = conn.execute("SELECT version FROM entries WHERE id = ?", (entry_id,)).fetchone()[0]
    assert new_version == old_version + 1, f"Version trigger failed. Expected {old_version + 1}, got {new_version}"
    print("Version trigger verification passed.")

def test_data_integrity():
    conn = sqlite3.connect(DB_PATH)
    # Check if grammar entries exist
    grammar_count = conn.execute("SELECT count(*) FROM grammar").fetchone()[0]
    assert grammar_count == 8, f"Expected 8 grammar entries, found {grammar_count}"
    print("Data integrity check passed.")

if __name__ == "__main__":
    try:
        test_schema_verification()
        test_version_triggers()
        test_data_integrity()
        print("ALL TESTS PASSED.")
    except Exception as e:
        print(f"TEST FAILED: {e}")
        sys.exit(1)
