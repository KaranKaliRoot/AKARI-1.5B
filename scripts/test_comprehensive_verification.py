"""Comprehensive 12-Category Verification Test Suite for AKARI Phase 7.1 Database."""

import sqlite3
import sys
import shutil
from pathlib import Path

# Ensure root directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

TEMP_DB = Path("data/temp_test.db")
PROD_DB = Path("data/akari.db")
BACKUP_DB = Path("data/akari.db.backup_20261108_190229")

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS provenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    license_name TEXT NOT NULL,
    license_url TEXT,
    license_text TEXT,
    version_tag TEXT NOT NULL,
    import_date TEXT NOT NULL,
    license_verification_date TEXT NOT NULL,
    verification_tier TEXT CHECK(verification_tier IN ('VERIFIED', 'PEER-REVIEWED', 'AUTOMATED')) NOT NULL,
    redistribution_notes TEXT
);

CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT CHECK(domain IN (
        'grammar', 'vocabulary', 'kanji', 'linguistics', 'pragmatics',
        'dialects', 'historical', 'literature', 'culture', 'modern',
        'professional', 'assessment'
    )) NOT NULL,
    jlpt_level TEXT CHECK(jlpt_level IN ('N5', 'N4', 'N3', 'N2', 'N1', 'NONE')) DEFAULT 'NONE',
    provenance_id INTEGER NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (provenance_id) REFERENCES provenance(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL,
    kana TEXT NOT NULL,
    kanji TEXT,
    reading_type TEXT CHECK(reading_type IN ('onyomi', 'kunyomi', 'nanori', 'standard', 'colloquial', 'archaic')) DEFAULT 'standard',
    is_primary INTEGER CHECK(is_primary IN (0, 1)) DEFAULT 0,
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS senses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL,
    sense_order INTEGER NOT NULL DEFAULT 1,
    glossary_en TEXT NOT NULL,
    pos_tag TEXT,
    register_tag TEXT,
    usage_restriction TEXT,
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS examples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL,
    japanese TEXT NOT NULL,
    reading TEXT,
    english TEXT NOT NULL,
    provenance_id INTEGER,
    license_name TEXT,
    contributor_attribution TEXT,
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE,
    FOREIGN KEY (provenance_id) REFERENCES provenance(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS grammar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER UNIQUE NOT NULL,
    pattern TEXT NOT NULL,
    formation TEXT NOT NULL,
    explanation TEXT NOT NULL,
    usage_notes TEXT,
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER UNIQUE NOT NULL,
    lemma TEXT NOT NULL,
    frequency_rank INTEGER,
    pitch_accent TEXT,
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS kanji (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER UNIQUE NOT NULL,
    character TEXT UNIQUE NOT NULL,
    stroke_count INTEGER NOT NULL,
    radical TEXT NOT NULL,
    grade INTEGER,
    etymology TEXT,
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE
);

CREATE TRIGGER IF NOT EXISTS trg_readings_insert AFTER INSERT ON readings
BEGIN UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = NEW.entry_id; END;

CREATE TRIGGER IF NOT EXISTS trg_readings_delete AFTER DELETE ON readings
BEGIN UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = OLD.entry_id; END;

CREATE TRIGGER IF NOT EXISTS trg_readings_update AFTER UPDATE ON readings
BEGIN
    UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = OLD.entry_id;
    UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = NEW.entry_id AND NEW.entry_id <> OLD.entry_id;
END;
"""

def setup_temp_db():
    if TEMP_DB.exists():
        TEMP_DB.unlink()
    conn = sqlite3.connect(TEMP_DB)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(SCHEMA)
    conn.commit()
    return conn

def test_cat1_schema_creation():
    conn = setup_temp_db()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    expected = ['entries', 'provenance', 'readings', 'senses', 'examples', 'grammar', 'vocabulary', 'kanji']
    for t in expected:
        assert t in tables, f"Missing table {t}"
    conn.close()
    print("Category 1 (Schema Creation): PASS")

def test_cat2_fk_enforcement():
    conn = setup_temp_db()
    try:
        conn.execute("INSERT INTO entries (domain, provenance_id) VALUES ('grammar', 9999);")
        assert False, "Should have failed FK constraint"
    except sqlite3.IntegrityError:
        print("Category 2 (Foreign-Key Enforcement): PASS")
    finally:
        conn.close()

def test_cat3_unique_constraints():
    conn = setup_temp_db()
    conn.execute("INSERT INTO provenance (source_name, source_url, license_name, version_tag, import_date, license_verification_date, verification_tier) VALUES ('a','b','c','d','e','f','AUTOMATED');")
    prov_id = 1
    conn.execute(f"INSERT INTO entries (domain, provenance_id) VALUES ('kanji', {prov_id});")
    conn.execute("INSERT INTO kanji (entry_id, character, stroke_count, radical) VALUES (1, '日', 4, '日');")

    try:
        conn.execute(f"INSERT INTO entries (domain, provenance_id) VALUES ('kanji', {prov_id});")
        conn.execute("INSERT INTO kanji (entry_id, character, stroke_count, radical) VALUES (2, '日', 4, '日');")
        assert False, "Should have failed UNIQUE constraint on kanji.character"
    except sqlite3.IntegrityError:
        print("Category 3 (Unique Constraints): PASS")
    finally:
        conn.close()

def test_cat4_invalid_relationship_rejection():
    conn = setup_temp_db()
    try:
        conn.execute("INSERT INTO examples (entry_id, japanese, english) VALUES (9999, 'a', 'b');")
        assert False, "Should have failed FK constraint on invalid entry_id"
    except sqlite3.IntegrityError:
        print("Category 4 (Invalid Relationship Rejection): PASS")
    finally:
        conn.close()

def test_cat5_insert_triggers():
    conn = setup_temp_db()
    conn.execute("INSERT INTO provenance (source_name, source_url, license_name, version_tag, import_date, license_verification_date, verification_tier) VALUES ('a','b','c','d','e','f','AUTOMATED');")
    conn.execute("INSERT INTO entries (domain, provenance_id) VALUES ('vocabulary', 1);")
    v1 = conn.execute("SELECT version FROM entries WHERE id = 1;").fetchone()[0]

    conn.execute("INSERT INTO readings (entry_id, kana) VALUES (1, 'たべる');")
    v2 = conn.execute("SELECT version FROM entries WHERE id = 1;").fetchone()[0]

    assert v2 == v1 + 1, f"Expected version {v1+1}, got {v2}"
    print("Category 5 (INSERT Version Triggers): PASS")
    conn.close()

def test_cat6_update_triggers():
    conn = setup_temp_db()
    conn.execute("INSERT INTO provenance (source_name, source_url, license_name, version_tag, import_date, license_verification_date, verification_tier) VALUES ('a','b','c','d','e','f','AUTOMATED');")
    conn.execute("INSERT INTO entries (domain, provenance_id) VALUES ('vocabulary', 1);")
    conn.execute("INSERT INTO readings (entry_id, kana) VALUES (1, 'たべる');")
    v1 = conn.execute("SELECT version FROM entries WHERE id = 1;").fetchone()[0]

    conn.execute("UPDATE readings SET kana = 'タベル' WHERE entry_id = 1;")
    v2 = conn.execute("SELECT version FROM entries WHERE id = 1;").fetchone()[0]

    assert v2 == v1 + 1, f"Expected version {v1+1}, got {v2}"
    print("Category 6 (UPDATE Version Triggers): PASS")
    conn.close()

def test_cat7_delete_triggers():
    conn = setup_temp_db()
    conn.execute("INSERT INTO provenance (source_name, source_url, license_name, version_tag, import_date, license_verification_date, verification_tier) VALUES ('a','b','c','d','e','f','AUTOMATED');")
    conn.execute("INSERT INTO entries (domain, provenance_id) VALUES ('vocabulary', 1);")
    conn.execute("INSERT INTO readings (entry_id, kana) VALUES (1, 'たべる');")
    v1 = conn.execute("SELECT version FROM entries WHERE id = 1;").fetchone()[0]

    conn.execute("DELETE FROM readings WHERE entry_id = 1;")
    v2 = conn.execute("SELECT version FROM entries WHERE id = 1;").fetchone()[0]

    assert v2 == v1 + 1, f"Expected version {v1+1}, got {v2}"
    print("Category 7 (DELETE Version Triggers): PASS")
    conn.close()

def test_cat8_reparenting_triggers():
    conn = setup_temp_db()
    conn.execute("INSERT INTO provenance (source_name, source_url, license_name, version_tag, import_date, license_verification_date, verification_tier) VALUES ('a','b','c','d','e','f','AUTOMATED');")
    conn.execute("INSERT INTO entries (domain, provenance_id) VALUES ('vocabulary', 1);")
    conn.execute("INSERT INTO entries (domain, provenance_id) VALUES ('vocabulary', 1);")
    conn.execute("INSERT INTO readings (entry_id, kana) VALUES (1, 'たべる');")

    v1_old = conn.execute("SELECT version FROM entries WHERE id = 1;").fetchone()[0]
    v2_old = conn.execute("SELECT version FROM entries WHERE id = 2;").fetchone()[0]

    conn.execute("UPDATE readings SET entry_id = 2 WHERE id = 1;")

    v1_new = conn.execute("SELECT version FROM entries WHERE id = 1;").fetchone()[0]
    v2_new = conn.execute("SELECT version FROM entries WHERE id = 2;").fetchone()[0]

    assert v1_new == v1_old + 1, "Old parent version should increment"
    assert v2_new == v2_old + 1, "New parent version should increment"
    print("Category 8 (Re-parenting Version Updates): PASS")
    conn.close()

def test_cat9_provenance_constraints():
    conn = setup_temp_db()
    try:
        conn.execute("INSERT INTO provenance (source_name, source_url, license_name, version_tag, import_date, license_verification_date, verification_tier) VALUES ('a','b','c','d','e','f','INVALID_TIER');")
        assert False, "Should have failed CHECK constraint on verification_tier"
    except sqlite3.IntegrityError:
        print("Category 9 (Provenance Constraints): PASS")
    finally:
        conn.close()

def test_cat10_migration_preservation():
    conn = sqlite3.connect(PROD_DB)
    g_count = conn.execute("SELECT count(*) FROM grammar;").fetchone()[0]
    v_count = conn.execute("SELECT count(*) FROM vocabulary;").fetchone()[0]
    assert g_count >= 8, f"Expected at least 8 grammar records, got {g_count}"
    assert v_count >= 6, f"Expected at least 6 vocabulary records, got {v_count}"
    print("Category 10 (Migration Preservation): PASS")
    conn.close()

def test_cat11_transaction_rollback():
    conn = setup_temp_db()
    try:
        with conn:
            conn.execute("INSERT INTO provenance (source_name, source_url, license_name, version_tag, import_date, license_verification_date, verification_tier) VALUES ('a','b','c','d','e','f','AUTOMATED');")
            conn.execute("INSERT INTO entries (domain, provenance_id) VALUES ('invalid_domain', 1);")
    except sqlite3.IntegrityError:
        pass

    count = conn.execute("SELECT count(*) FROM provenance;").fetchone()[0]
    assert count == 0, "Transaction rollback failed, record persisted"
    print("Category 11 (Transaction Rollback): PASS")
    conn.close()

def test_cat12_database_integrity():
    conn = sqlite3.connect(PROD_DB)
    res = conn.execute("PRAGMA integrity_check;").fetchone()[0]
    assert res == "ok", f"Integrity check failed: {res}"
    print("Category 12 (Database Integrity Checks): PASS")
    conn.close()

def test_backup_restore():
    assert BACKUP_DB.exists(), "Backup DB does not exist!"
    conn = sqlite3.connect(BACKUP_DB)
    res = conn.execute("SELECT count(*) FROM grammar;").fetchone()[0]
    assert res == 8, "Backup file incomplete"
    conn.close()
    print("Backup Restoration Check: PASS")

def test_backend_live_compatibility():
    from backend.database import AkariDB
    db = AkariDB()
    g = db.search_grammar("〜ている")
    v = db.search_vocabulary("食べる")
    assert len(g) > 0, "Backend grammar query failed"
    assert len(v) > 0, "Backend vocab query failed"
    print("Backend Compatibility Check: PASS")

if __name__ == "__main__":
    print("--- RUNNING FULL 12-CATEGORY VERIFICATION ---")
    test_cat1_schema_creation()
    test_cat2_fk_enforcement()
    test_cat3_unique_constraints()
    test_cat4_invalid_relationship_rejection()
    test_cat5_insert_triggers()
    test_cat6_update_triggers()
    test_cat7_delete_triggers()
    test_cat8_reparenting_triggers()
    test_cat9_provenance_constraints()
    test_cat10_migration_preservation()
    test_cat11_transaction_rollback()
    test_cat12_database_integrity()
    test_backup_restore()
    test_backend_live_compatibility()

    if TEMP_DB.exists():
        TEMP_DB.unlink()
    print("--- ALL 12 CATEGORIES VERIFIED PERFECTLY ---")
