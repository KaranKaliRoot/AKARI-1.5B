# AKARI Knowledge Base: SQLite Schema Design (Phase 6.3)

The AKARI database schema uses a normalized relational architecture anchored by an `entries` table, supporting all 12 knowledge domains through core sub-tables and specialized domain extension tables.

---

## 1. Relational Integrity & Configuration

All connections to SQLite MUST execute the following pragma upon opening a session:
```sql
PRAGMA foreign_keys = ON;
```

---

## 2. Conceptual Schema Overview

```text
                               +-------------------------+
                               |       provenance        |
                               +-------------------------+
                                      |             \ (override 1:N)
                             (1:N)    v              v
+------------------+          +-------------------------+          +------------------+
|     readings     | <------- |         entries         | -------> |      senses      |
+------------------+          +-------------------------+          +------------------+
(inherits prov)                       | (1:1 / 1:N)                (inherits prov)
        +-----------------------------+-----------------------------+
        |                             |                             |
        v                             v                             v
+------------------+         +------------------+         +------------------+
|     grammar      |         |    vocabulary    |         |      kanji       |
+------------------+         +------------------+         +------------------+
        |                             |                             |
        +-----------------------------+-----------------------------+
        | (1:N)                       | (1:N)                       | (1:N)
        v                             v                             v
+-------------------------------------------------------------------------------------+
|                                      examples                                       |
|                  (has direct provenance_id override & attribution)                   |
+-------------------------------------------------------------------------------------+
```

---

## 3. Core Relational Tables

### 3.1 `provenance` (Data Source & License Registry)
```sql
CREATE TABLE provenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    license_name TEXT NOT NULL,
    license_url TEXT,
    license_text TEXT,
    version_tag TEXT NOT NULL,
    import_date TEXT NOT NULL, -- ISO 8601 UTC
    license_verification_date TEXT NOT NULL, -- ISO 8601 UTC
    verification_tier TEXT CHECK(verification_tier IN ('VERIFIED', 'PEER-REVIEWED', 'AUTOMATED')) NOT NULL,
    redistribution_notes TEXT
);
```

### 3.2 `entries` (Central Relational Anchor)
```sql
CREATE TABLE entries (
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

CREATE INDEX idx_entries_domain ON entries(domain);
CREATE INDEX idx_entries_jlpt ON entries(jlpt_level);
```

---

## 4. Shared Linguistic Sub-Tables & Provenance Rules

### 4.1 Provenance Inheritance Rules
- **Inherited Provenance:** `readings` and `senses` do not contain a `provenance_id` column; they implicitly inherit the dataset provenance of their parent `entries.provenance_id`.
- **Direct Provenance Override:** `examples` contains an explicit `provenance_id` and `contributor_attribution` column. If `examples.provenance_id` is set, it overrides `entries.provenance_id`. This preserves sentence-level licensing and individual contributor attributions (e.g., Tatoeba).

### 4.2 Shared Sub-Tables
```sql
CREATE TABLE readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL,
    kana TEXT NOT NULL,
    kanji TEXT,
    reading_type TEXT CHECK(reading_type IN ('onyomi', 'kunyomi', 'nanori', 'standard', 'colloquial', 'archaic')) DEFAULT 'standard',
    is_primary INTEGER CHECK(is_primary IN (0, 1)) DEFAULT 0,
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE
);
CREATE INDEX idx_readings_kana ON readings(kana);
CREATE INDEX idx_readings_kanji ON readings(kanji);

CREATE TABLE senses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL,
    sense_order INTEGER NOT NULL DEFAULT 1,
    glossary_en TEXT NOT NULL,
    pos_tag TEXT,
    register_tag TEXT,
    usage_restriction TEXT,
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE
);
CREATE INDEX idx_senses_entry ON senses(entry_id);

CREATE TABLE examples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL,
    japanese TEXT NOT NULL,
    reading TEXT,
    english TEXT NOT NULL,
    provenance_id INTEGER, -- Mandatory for imported example datasets
    license_name TEXT,     -- Mandatory for imported example datasets
    contributor_attribution TEXT, -- Mandatory for Tatoeba/volunteer datasets
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE,
    FOREIGN KEY (provenance_id) REFERENCES provenance(id) ON DELETE RESTRICT
);
CREATE INDEX idx_examples_entry ON examples(entry_id);
```

**Tatoeba Attribution Enforcement:** 
To ensure legal compliance with Tatoeba and other volunteer-sourced datasets, the ingestion layer MUST enforce the presence of `provenance_id`, `license_name`, and `contributor_attribution`. Incomplete records MUST be quarantined and skipped; silent acceptance of records without source attribution is strictly prohibited.

---

## 5. Domain-Specific SQL Tables

### 5.1 Primary Implemented Specialized Tables
These tables extend the core `entries` schema for domains requiring unique structural attributes.
```sql
CREATE TABLE grammar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER UNIQUE NOT NULL,
    pattern TEXT NOT NULL,
    formation TEXT NOT NULL,
    explanation TEXT NOT NULL,
    usage_notes TEXT,
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE
);

CREATE TABLE vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER UNIQUE NOT NULL,
    lemma TEXT NOT NULL,
    frequency_rank INTEGER,
    pitch_accent TEXT,
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE
);

CREATE TABLE kanji (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER UNIQUE NOT NULL,
    character TEXT UNIQUE NOT NULL,
    stroke_count INTEGER NOT NULL,
    radical TEXT NOT NULL,
    grade INTEGER,
    etymology TEXT,
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE
);

CREATE TABLE kanji_components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_kanji_id INTEGER NOT NULL,
    child_kanji_id INTEGER NOT NULL,
    component_role TEXT,
    FOREIGN KEY (parent_kanji_id) REFERENCES kanji(id) ON DELETE CASCADE,
    FOREIGN KEY (child_kanji_id) REFERENCES kanji(id) ON DELETE CASCADE,
    UNIQUE(parent_kanji_id, child_kanji_id)
);

CREATE TABLE cross_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_entry_id INTEGER NOT NULL,
    target_entry_id INTEGER NOT NULL,
    relation_type TEXT CHECK(relation_type IN ('synonym', 'antonym', 'similar_grammar', 'kanji_compound', 'pragmatic_pair', 'historical_ancestor')) NOT NULL,
    FOREIGN KEY (source_entry_id) REFERENCES entries(id) ON DELETE CASCADE,
    FOREIGN KEY (target_entry_id) REFERENCES entries(id) ON DELETE CASCADE,
    UNIQUE(source_entry_id, target_entry_id, relation_type)
);
```

### 5.2 Extended Domain Specialized Tables
```sql
CREATE TABLE linguistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER UNIQUE NOT NULL,
    phonetic_ipa TEXT,
    mora_count INTEGER,
    mora_structure TEXT,
    morphological_class TEXT,
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE
);

CREATE TABLE dialects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL,
    dialect_name TEXT NOT NULL, -- e.g., Kansai-ben, Tohoku-ben
    standard_equivalent TEXT,
    regional_description TEXT,
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE
);

CREATE TABLE assessment_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_option TEXT CHECK(correct_option IN ('A', 'B', 'C', 'D')) NOT NULL,
    explanation TEXT NOT NULL,
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE
);
```

### 5.3 Shared Core Mapping for Remaining Domains
The remaining domains (**Pragmatics, Historical Japanese, Literature, Culture, Modern/Slang, Professional Japanese**) are fully supported without extra table overhead by utilizing `entries(domain=...)` paired with `readings`, `senses(register_tag, usage_restriction)`, and `examples`. No extra specialized tables are required for these 6 domains.

---

## 6. Version Increment Triggers

To ensure parent `entries.version` increments automatically whenever child records are added, modified, or removed, the following SQLite triggers are required for `readings`, `senses`, and `examples`. Similar triggers should be applied to specialized domain tables (`grammar`, `vocabulary`, etc.).

### 6.1 Child Table Version Triggers
The following triggers MUST be defined for `readings`, `senses`, and `examples`. (Similar triggers should be applied to specialized domain tables like `grammar`, `vocabulary`, etc.)

#### Triggers for `readings`
```sql
CREATE TRIGGER trg_readings_insert AFTER INSERT ON readings
BEGIN
    UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = NEW.entry_id;
END;

CREATE TRIGGER trg_readings_delete AFTER DELETE ON readings
BEGIN
    UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = OLD.entry_id;
END;

CREATE TRIGGER trg_readings_update AFTER UPDATE ON readings
BEGIN
    UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = OLD.entry_id;
    UPDATE entries SET version = version + 1, updated_at = datetime('now') 
    WHERE id = NEW.entry_id AND NEW.entry_id <> OLD.entry_id;
END;
```

#### Triggers for `senses`
```sql
CREATE TRIGGER trg_senses_insert AFTER INSERT ON senses
BEGIN
    UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = NEW.entry_id;
END;

CREATE TRIGGER trg_senses_delete AFTER DELETE ON senses
BEGIN
    UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = OLD.entry_id;
END;

CREATE TRIGGER trg_senses_update AFTER UPDATE ON senses
BEGIN
    UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = OLD.entry_id;
    UPDATE entries SET version = version + 1, updated_at = datetime('now') 
    WHERE id = NEW.entry_id AND NEW.entry_id <> OLD.entry_id;
END;
```

#### Triggers for `examples`
```sql
CREATE TRIGGER trg_examples_insert AFTER INSERT ON examples
BEGIN
    UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = NEW.entry_id;
END;

CREATE TRIGGER trg_examples_delete AFTER DELETE ON examples
BEGIN
    UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = OLD.entry_id;
END;

CREATE TRIGGER trg_examples_update AFTER UPDATE ON examples
BEGIN
    UPDATE entries SET version = version + 1, updated_at = datetime('now') WHERE id = OLD.entry_id;
    UPDATE entries SET version = version + 1, updated_at = datetime('now') 
    WHERE id = NEW.entry_id AND NEW.entry_id <> OLD.entry_id;
END;
```

### 6.2 Recursive Safety & Lifecycle Rules
1. **Recursion Prevention:** These triggers update the `entries` table directly. Since there are no triggers on `entries` that modify child tables, infinite recursion is prevented. (Note: `PRAGMA recursive_triggers = OFF` is the SQLite default).
2. **Direct Entry Updates:** Modifications to columns in the `entries` table itself (e.g., changing `jlpt_level`) must explicitly increment the `version` column as part of the `UPDATE` statement.
3. **Trigger Implementation:** Application-level transactions must wrap batch child operations to ensure atomicity, but the `version` increment is guaranteed at the database level by these triggers.
