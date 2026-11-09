# AKARI Knowledge Base: Retrieval & Intelligence Pipeline (Phase 6.3)

This document defines query processing, character normalization, FTS5 detection, multi-key search execution, ranking, and prompt context formatting for Qwen2.5-1.5B.

---

## 1. Multi-Key Preprocessing & Character Normalization

When a user submits a query in `teaching` mode, the preprocessor generates multiple candidate search keys while **preserving the original query string intact** for downstream display and exact-matching.

### 1.1 Key Generation Pipeline
1. **Original Query Key ($K_{\text{orig}}$):** Unaltered user input (e.g., `「食べる」`).
2. **Normalized Character Key ($K_{\text{norm}}$):**
   - Full-width alphanumeric to half-width ASCII.
   - Variant kanji to standard 常用漢字.
3. **Kana-Standardized Key ($K_{\text{kana}}$):**
   - Converts Katakana substrings to Hiragana (e.g., `タベル` $\rightarrow$ `たべる`).
4. **Romaji/Alpha Key ($K_{\text{romaji}}$):**
   - Converts Hepburn romaji input to Hiragana equivalent if applicable.

All generated keys ($K_{\text{orig}}, K_{\text{norm}}, K_{\text{kana}}, K_{\text{romaji}}$) are queried in parallel across database search stages.

---

## 2. Dynamic FTS5 & Tokenizer Capability Probe

To determine FTS5 availability and supported tokenizers at runtime without hardcoding system assumptions, `backend/database.py` executes temporary virtual table creation tests upon startup:

```python
def detect_fts_capabilities(db_connection):
    capabilities = {"fts5": False, "trigram": False}
    cursor = db_connection.cursor()
    
    # Test 1: Probe FTS5 support
    try:
        cursor.execute("CREATE VIRTUAL TABLE temp.fts_probe USING fts5(content);")
        cursor.execute("DROP TABLE temp.fts_probe;")
        capabilities["fts5"] = True
    except sqlite3.OperationalError:
        return capabilities # FTS5 unavailable

    # Test 2: Probe Trigram Tokenizer support
    try:
        cursor.execute("CREATE VIRTUAL TABLE temp.fts_trigram_probe USING fts5(content, tokenize='trigram');")
        cursor.execute("DROP TABLE temp.fts_trigram_probe;")
        capabilities["trigram"] = True
    except sqlite3.OperationalError:
        capabilities["trigram"] = False # Trigram unavailable, fallback to default tokenizer

    return capabilities
```

- **If FTS5 + Trigram:** Use trigram index on Japanese text.
- **If FTS5 + unicode61:** Use default unicode tokenizer (Note: `unicode61` splits on whitespace/punctuation and does NOT perform Japanese morphological tokenization; requires supplementary substring matching).
- **If FTS5 Unavailable:** Fall back to Stage 3 SQL `LIKE %query%` pattern matching.

---

## 3. Four-Stage Retrieval Hierarchy

```text
Stage 1: Exact Match (pattern, lemma, character, reading)
   │
   ├── (0 hits) ──► Stage 2: SQLite FTS5 (Trigram / unicode61)
   │                   │
   │                   ├── (0 hits) ──► Stage 3: Substring SQL LIKE %query%
   │                   │                   │
   ▼                   ▼                   └── (0 hits) ──► Stage 4: Unbacked General LLM Generation
```

---

## 4. Deterministic Scoring & Tie-Breaking Algorithm

Candidate records retrieved across search keys and stages are scored using a deterministic formula:

$$\text{Final Score} = S_{\text{match}} + S_{\text{jlpt}} + S_{\text{provenance}}$$

### 4.1 Match Weights ($S_{\text{match}}$)
- **100 pts:** Exact match on $K_{\text{orig}}$ against `grammar.pattern`, `vocabulary.lemma`, or `kanji.character`.
- **85 pts:** Exact match on $K_{\text{kana}}$ or $K_{\text{norm}}$ against `readings.kana` or `readings.kanji`.
- **60 pts:** FTS5 match using $K_{\text{orig}}$ or $K_{\text{kana}}$.
- **40 pts:** SQL `LIKE %query%` partial substring match.

### 4.2 Attribute Bonus Weights
- **+$S_{\text{jlpt}}$ (15 pts):** Match with user's target JLPT level.
- **+$S_{\text{provenance}}$ (20 pts):** `VERIFIED` tier provenance (`+10` for `PEER-REVIEWED`, `+0` for `AUTOMATED`).

### 4.3 Deterministic Tie-Breaking Order
If multiple candidate records share an identical `Final Score`, ties are resolved using a multi-step deterministic order:

1. **Provenance Tier (Higher First):** `VERIFIED` > `PEER-REVIEWED` > `AUTOMATED`.
2. **Vocabulary Frequency Rank (`NULLS LAST`):**
   - Applies *only* to candidates in the `vocabulary` domain (or candidates with a linked `vocabulary` record). Non-vocabulary candidates (e.g., grammar, kanji, pragmatics) or vocabulary records where `frequency_rank IS NULL` are assigned a rank of `NULL`.
   - Lower numeric rank indicates higher usage frequency (e.g., Rank 1 > Rank 500). Candidates with non-NULL frequency ranks are ordered ascending (`frequency_rank ASC`).
   - Candidates without frequency information are sorted after all ranked vocabulary entries (`NULLS LAST`).
3. **Primary Entry Identifier (`entries.id ASC`):**
   - For any candidates that remain tied (including all non-vocabulary candidates or entries with identical frequency ranks), the tie is broken by sorting by `entries.id ASC` (oldest/canonical entry first).

---

## 5. Zero-Hit Behavior & System Prompt Formatting

If Stages 1–3 yield zero hits, AKARI formats the system prompt with explicit instructions to prevent hallucinating database entries:

```text
[RETRIEVED KNOWLEDGE BASE CONTEXT]
No verified local database entries matched the query.
INSTRUCTION: Answer using general background knowledge. You MUST include this notice to the user:
"Note: This explanation is based on my general training rather than a verified local database record."
```
