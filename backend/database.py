"""AKARI Database Access Layer.
Handles SQLite-based storage for Japanese grammar, vocabulary, and kanji using the Phase 6.3 normalized schema.
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict

DB_PATH = Path(__file__).parent.parent / "data" / "akari.db"

class AkariDB:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    def _normalize_query(self, query: str) -> str:
        kana_norm = "".join([chr(ord(c) - 96) if 'ァ' <= c <= 'ヶ' else c for c in query])
        full_to_half = {
            chr(i): chr(i - 0xFEE0) for i in range(0xFF01, 0xFF5F)
        }
        normalized = kana_norm.translate(str.maketrans(full_to_half))
        return normalized.translate(str.maketrans("", "", "、。！？!?.,"))

    def search_all_domains(self, query: str) -> List[Dict]:
        """Comprehensive search across all 12 domains."""
        clean_query = self._normalize_query(query)
        search_pattern = f"%{clean_query}%"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            grammar_sql = """
                SELECT 'grammar' as domain, g.pattern as key, g.explanation as details, s.glossary_en as meaning
                FROM grammar g
                JOIN entries e ON g.entry_id = e.id
                LEFT JOIN senses s ON s.entry_id = e.id
                WHERE g.pattern LIKE ? OR g.explanation LIKE ?
            """
            vocab_sql = """
                SELECT 'vocabulary' as domain, v.lemma as key, s.glossary_en as details, 'N/A' as meaning
                FROM vocabulary v
                JOIN entries e ON v.entry_id = e.id
                LEFT JOIN senses s ON s.entry_id = e.id
                WHERE v.lemma LIKE ?
            """
            cursor = conn.cursor()
            results = []
            for sql in [grammar_sql, vocab_sql]:
                cursor.execute(sql, (search_pattern, search_pattern) if sql == grammar_sql else (search_pattern,))
                results.extend([dict(row) for row in cursor.fetchall()])
            return results

    def search_grammar(self, query: str, jlpt_level: Optional[int] = None) -> List[Dict]:
        """Backward compatible grammar search."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            sql = """
                SELECT g.pattern, g.explanation, s.glossary_en AS meaning
                FROM grammar g
                JOIN entries e ON g.entry_id = e.id
                LEFT JOIN senses s ON s.entry_id = e.id
                WHERE (g.pattern LIKE ? OR g.explanation LIKE ? OR s.glossary_en LIKE ?)
            """
            params = [f"%{query}%", f"%{query}%", f"%{query}%"]
            if jlpt_level:
                sql += " AND e.jlpt_level = ?"
                params.append(f"N{jlpt_level}")
            cursor = conn.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

    def search_vocabulary(self, query: str, jlpt_level: Optional[int] = None) -> List[Dict]:
        """Backward compatible vocabulary search."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            sql = """
                SELECT v.lemma AS word, r.kana AS reading, r.kanji AS kanji, s.glossary_en AS meaning, s.pos_tag AS pos
                FROM vocabulary v
                JOIN entries e ON v.entry_id = e.id
                LEFT JOIN readings r ON r.entry_id = e.id
                LEFT JOIN senses s ON s.entry_id = e.id
                WHERE (v.lemma LIKE ? OR r.kana LIKE ? OR r.kanji LIKE ? OR s.glossary_en LIKE ?)
            """
            params = [f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"]
            if jlpt_level:
                sql += " AND e.jlpt_level = ?"
                params.append(f"N{jlpt_level}")
            cursor = conn.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]
