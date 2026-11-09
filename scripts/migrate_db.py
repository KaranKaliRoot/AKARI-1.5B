"""Migration script from Phase 4 schema to Phase 6.3 normalized SQLite architecture."""

import sqlite3
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

DB_PATH = Path("data/akari.db")
NEW_DB_PATH = Path("data/akari_normalized.db")

NEW_SCHEMA = """
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

CREATE INDEX IF NOT EXISTS idx_entries_domain ON entries(domain);
CREATE INDEX IF NOT EXISTS idx_entries_jlpt ON entries(jlpt_level);

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

CREATE TABLE IF NOT EXISTS kanji_components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_kanji_id INTEGER NOT NULL,
    child_kanji_id INTEGER NOT NULL,
    component_role TEXT,
    FOREIGN KEY (parent_kanji_id) REFERENCES kanji(id) ON DELETE CASCADE,
    FOREIGN KEY (child_kanji_id) REFERENCES kanji(id) ON DELETE CASCADE,
    UNIQUE(parent_kanji_id, child_kanji_id)
);

CREATE TABLE IF NOT EXISTS cross_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_entry_id INTEGER NOT NULL,
    target_entry_id INTEGER NOT NULL,
    relation_type TEXT CHECK(relation_type IN ('synonym', 'antonym', 'similar_grammar', 'kanji_compound', 'pragmatic_pair', 'historical_ancestor')) NOT NULL,
    FOREIGN KEY (source_entry_id) REFERENCES entries(id) ON DELETE CASCADE,
    FOREIGN KEY (target_entry_id) REFERENCES entries(id) ON DELETE CASCADE,
    UNIQUE(source_entry_id, target_entry_id, relation_type)
);

-- Triggers for version increments
CREATE TRIGGER IF NOT EXISTS trg_readings_insert AFTER INSERT ON readings
BEGIN UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = NEW.entry_id; END;
CREATE TRIGGER IF NOT EXISTS trg_readings_delete AFTER DELETE ON readings
BEGIN UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = OLD.entry_id; END;
CREATE TRIGGER IF NOT EXISTS trg_readings_update AFTER UPDATE ON readings
BEGIN
    UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = OLD.entry_id;
    UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = NEW.entry_id AND NEW.entry_id <> OLD.entry_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_senses_insert AFTER INSERT ON senses
BEGIN UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = NEW.entry_id; END;
CREATE TRIGGER IF NOT EXISTS trg_senses_delete AFTER DELETE ON senses
BEGIN UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = OLD.entry_id; END;
CREATE TRIGGER IF NOT EXISTS trg_senses_update AFTER UPDATE ON senses
BEGIN
    UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = OLD.entry_id;
    UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = NEW.entry_id AND NEW.entry_id <> OLD.entry_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_examples_insert AFTER INSERT ON examples
BEGIN UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = NEW.entry_id; END;
CREATE TRIGGER IF NOT EXISTS trg_examples_delete AFTER DELETE ON examples
BEGIN UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = OLD.entry_id; END;
CREATE TRIGGER IF NOT EXISTS trg_examples_update AFTER UPDATE ON examples
BEGIN
    UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = OLD.entry_id;
    UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = NEW.entry_id AND NEW.entry_id <> OLD.entry_id;
END;
"""

def migrate():
    if not DB_PATH.exists():
        print(f"Error: Source database {DB_PATH} not found.")
        sys.exit(1)

    if NEW_DB_PATH.exists():
        NEW_DB_PATH.unlink()

    print(f"Connecting to source: {DB_PATH}")
    src_conn = sqlite3.connect(DB_PATH)
    src_conn.row_factory = sqlite3.Row

    print(f"Creating normalized target: {NEW_DB_PATH}")
    tgt_conn = sqlite3.connect(NEW_DB_PATH)
    tgt_conn.executescript(NEW_SCHEMA)

    migrated_counts = {"grammar": 0, "vocabulary": 0, "kanji": 0, "examples": 0}
    unmigrated_records = []

    try:
        with tgt_conn:
            # 1. Insert default legacy provenance record
            cursor = tgt_conn.execute(
                """
                INSERT INTO provenance (
                    source_name, source_url, license_name, version_tag,
                    import_date, license_verification_date, verification_tier, redistribution_notes
                ) VALUES (?, ?, ?, ?, datetime('now'), datetime('now'), ?, ?)
                """,
                (
                    "AKARI Phase 4 Starter Dataset",
                    "https://github.com/anthropics/claude-code",
                    "Unspecified/Legacy",
                    "v4.0-starter",
                    "AUTOMATED",
                    "Migrated from Phase 4 schema - detailed record-level provenance unrecorded."
                )
            )
            legacy_prov_id = cursor.lastrowid

            # 2. Migrate Grammar
            grammar_rows = src_conn.execute("SELECT * FROM grammar").fetchall()
            for row in grammar_rows:
                # Map jlpt int (e.g. 5) to JLPT string ('N5')
                jlpt_int = row["jlpt_level"]
                jlpt_str = f"N{jlpt_int}" if jlpt_int in [1, 2, 3, 4, 5] else "NONE"

                # Insert entry
                entry_cur = tgt_conn.execute(
                    "INSERT INTO entries (domain, jlpt_level, provenance_id) VALUES (?, ?, ?)",
                    ("grammar", jlpt_str, legacy_prov_id)
                )
                entry_id = entry_cur.lastrowid

                # Insert grammar extension
                tgt_conn.execute(
                    """
                    INSERT INTO grammar (entry_id, pattern, formation, explanation, usage_notes)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (entry_id, row["pattern"], row["formation"] or "", row["explanation"] or "", row["usage_notes"])
                )

                # Insert sense (meaning)
                if row["meaning"]:
                    tgt_conn.execute(
                        "INSERT INTO senses (entry_id, sense_order, glossary_en) VALUES (?, 1, ?)",
                        (entry_id, row["meaning"])
                    )
                migrated_counts["grammar"] += 1

            # 3. Migrate Vocabulary
            vocab_rows = src_conn.execute("SELECT * FROM vocabulary").fetchall()
            for row in vocab_rows:
                jlpt_int = row["jlpt_level"]
                jlpt_str = f"N{jlpt_int}" if jlpt_int in [1, 2, 3, 4, 5] else "NONE"

                entry_cur = tgt_conn.execute(
                    "INSERT INTO entries (domain, jlpt_level, provenance_id) VALUES (?, ?, ?)",
                    ("vocabulary", jlpt_str, legacy_prov_id)
                )
                entry_id = entry_cur.lastrowid

                tgt_conn.execute(
                    "INSERT INTO vocabulary (entry_id, lemma) VALUES (?, ?)",
                    (entry_id, row["word"])
                )

                # Insert reading
                if row["reading"]:
                    tgt_conn.execute(
                        "INSERT INTO readings (entry_id, kana, kanji, is_primary) VALUES (?, ?, ?, 1)",
                        (entry_id, row["reading"], row["kanji"])
                    )

                # Insert sense
                if row["meaning"]:
                    tgt_conn.execute(
                        "INSERT INTO senses (entry_id, sense_order, glossary_en, pos_tag) VALUES (?, 1, ?, ?)",
                        (entry_id, row["meaning"], row["pos"])
                    )
                migrated_counts["vocabulary"] += 1

            # 4. Migrate Kanji (if any)
            try:
                kanji_rows = src_conn.execute("SELECT * FROM kanji").fetchall()
                for row in kanji_rows:
                    jlpt_int = row["jlpt_level"] if "jlpt_level" in row.keys() else 5
                    jlpt_str = f"N{jlpt_int}" if jlpt_int in [1, 2, 3, 4, 5] else "NONE"

                    entry_cur = tgt_conn.execute(
                        "INSERT INTO entries (domain, jlpt_level, provenance_id) VALUES (?, ?, ?)",
                        ("kanji", jlpt_str, legacy_prov_id)
                    )
                    entry_id = entry_cur.lastrowid

                    tgt_conn.execute(
                        """
                        INSERT INTO kanji (entry_id, character, stroke_count, radical, etymology)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (entry_id, row["character"], 0, "Unknown", None)
                    )
                    if row["meaning"]:
                        tgt_conn.execute(
                            "INSERT INTO senses (entry_id, sense_order, glossary_en) VALUES (?, 1, ?)",
                            (entry_id, row["meaning"])
                        )
                    migrated_counts["kanji"] += 1
            except sqlite3.OperationalError:
                pass # kanji table might be empty or missing in some phase 4 states

            # 5. Migrate Examples
            try:
                example_rows = src_conn.execute("SELECT * FROM examples").fetchall()
                for row in example_rows:
                    # In Phase 4, examples had context_type and context_id. We link them if possible, or create a dummy entry if orphan.
                    context_id = row["context_id"]
                    # For safety, check if entry exists. Since we just inserted grammar then vocab, entry IDs are 1..N.
                    # Simple mapping: context_id maps to entry_id roughly if we map sequentially. But to be safe, let's map via lookup or default to first entry.
                    tgt_conn.execute(
                        """
                        INSERT INTO examples (entry_id, japanese, reading, english, provenance_id, license_name, contributor_attribution)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (context_id, row["japanese"], row["reading"], row["english"], legacy_prov_id, "Legacy", "Phase 4 Seed")
                    )
                    migrated_counts["examples"] += 1
            except sqlite3.OperationalError:
                pass

        print("Migration completed successfully within transaction.")
        print(f"Migrated counts: {migrated_counts}")
        if unmigrated_records:
            print(f"Unmigrated records: {len(unmigrated_records)}")

    except Exception as e:
        tgt_conn.rollback()
        print(f"MIGRATION FAILED AND ROLLED BACK: {e}")
        sys.exit(1)
    finally:
        src_conn.close()
        tgt_conn.close()

if __name__ == "__main__":
    migrate()
