"""Starter dataset seed script for AKARI Knowledge Base."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "akari.db"

SEED_DATA = [
    {
        "table": "grammar",
        "data": [
            ("〜ている", 5, "Continuous action or state", "Verb-te + いる", "Indicates an action currently in progress or a resulting state.", "Common for everyday habits and ongoing actions.", "Verified JLPT N5 reference dataset"),
            ("〜たい", 5, "Want to do something", "Verb-masu stem + たい", "Expresses the speaker's desire to do an action.", "Conates like an i-adjective.", "Verified JLPT N5 reference dataset"),
            ("〜なければならない", 4, "Must do / Have to", "Verb-nai stem + なければならない", "Expresses obligation or necessity.", "Often shortened to なきゃいけない in casual speech.", "Verified JLPT N4 reference dataset"),
            ("〜かもしれない", 4, "Might / May / It is possible that", "Plain form + かもしれない", "Expresses uncertainty or possibility (around 50% chance).", "More formal than でしょう or かも.", "Verified JLPT N4 reference dataset"),
            ("〜ことにしている", 3, "Make it a rule to / Decide to", "Verb-dictionary/nai + ことにしている", "Expresses a deliberate personal habit or ongoing rule adopted by the speaker.", "Used for conscious regular actions.", "Verified JLPT N3 reference dataset"),
            ("〜わけではない", 3, "It does not mean that / It is not the case that", "Plain form + わけではない", "Used to partially negate a statement or refute an assumption.", "Also used for polite mitigation.", "Verified JLPT N3 reference dataset"),
            ("〜ざるを得ない", 2, "Have no choice but to / Compelled to", "Verb-nai stem (except する -> せざるを得ない) + ざるを得ない", "Expresses doing something against one's preference due to circumstances.", "Formal written/spoken expression.", "Verified JLPT N2 reference dataset"),
            ("〜極まりない", 1, "Extremely / Absolute / The height of", "Na-adjective stem / Noun + 極まりない", "Expresses an extreme degree of a feeling or state, usually negative.", "Literary and formal expression.", "Verified JLPT N1 reference dataset"),
        ]
    },
    {
        "table": "vocabulary",
        "data": [
            ("食べる", "たべる", "食べる", "to eat", "Verb (Ru)", 5, "Verified reference"),
            ("飲む", "のむ", "飲む", "to drink", "Verb (U)", 5, "Verified reference"),
            ("勉強", "べんきょう", "勉強", "study / diligence", "Noun / Verb", 5, "Verified reference"),
            ("環境", "かんきょう", "環境", "environment / surroundings", "Noun", 3, "Verified reference"),
            ("貢献", "こうけん", "貢献", "contribution / service", "Noun / Verb", 2, "Verified reference"),
            ("喧嘩", "けんか", "喧嘩", "quarrel / fight / dispute", "Noun / Verb", 3, "Verified reference"),
        ]
    }
]

def seed_database():
    with sqlite3.connect(DB_PATH) as conn:
        for group in SEED_DATA:
            table = group["table"]
            if table == "grammar":
                for row in group["data"]:
                    conn.execute(
                        "INSERT OR IGNORE INTO grammar (pattern, jlpt_level, meaning, formation, explanation, usage_notes, provenance) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        row
                    )
            elif table == "vocabulary":
                for row in group["data"]:
                    conn.execute(
                        "INSERT OR IGNORE INTO vocabulary (word, reading, kanji, meaning, pos, jlpt_level, provenance) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        row
                    )
        conn.commit()
    print("Database seeded successfully.")

if __name__ == "__main__":
    seed_database()
