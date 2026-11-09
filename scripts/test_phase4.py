"""Phase 4 Automated Test Suite for AKARI Knowledge Base and Retrieval System."""

import json
import sqlite3
import sys
from pathlib import Path

# Force UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "data" / "akari.db"

def run_tests():
    print("=" * 60)
    print("AKARI Phase 4 Test Suite")
    print("=" * 60)

    # 1. Database File & Schema Check
    print("\n1. Database File & Schema Check")
    if DB_PATH.exists():
        print(f"   Database file exists: {DB_PATH}")
    else:
        print(f"   ERROR: Database file not found at {DB_PATH}")
        return

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r[0] for r in cursor.fetchall()]
        print(f"   Tables found: {tables}")

        # 2. Grammar Count by Level
        print("\n2. Grammar Entries by JLPT Level")
        cursor.execute("SELECT jlpt_level, COUNT(*) FROM grammar GROUP BY jlpt_level ORDER BY jlpt_level DESC;")
        for level, count in cursor.fetchall():
            print(f"   JLPT N{level}: {count} entry/entries")

        # 3. Vocabulary Count by Level
        print("\n3. Vocabulary Entries by JLPT Level")
        cursor.execute("SELECT jlpt_level, COUNT(*) FROM vocabulary GROUP BY jlpt_level ORDER BY jlpt_level DESC;")
        for level, count in cursor.fetchall():
            print(f"   JLPT N{level}: {count} entry/entries")

        # 4. Search Functionality Check
        print("\n4. Search Functionality Verification")
        # Search grammar
        cursor.execute("SELECT pattern, meaning FROM grammar WHERE pattern LIKE '%ている%';")
        row = cursor.fetchone()
        print(f"   Grammar Search Result ('ている'): {row[0]} -> {row[1]}")

        # Search vocabulary
        cursor.execute("SELECT word, meaning, pos FROM vocabulary WHERE word LIKE '%環境%';")
        row = cursor.fetchone()
        print(f"   Vocab Search Result ('環境'): {row[0]} -> {row[1]} ({row[2]})")

    print("\n" + "=" * 60)
    print("Phase 4 Verification Complete")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
