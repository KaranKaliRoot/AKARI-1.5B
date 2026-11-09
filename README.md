# AKARI (灯り) - Offline Japanese AI Tutor & Knowledge Engine

AKARI is an offline-first, multi-domain Japanese AI tutor powered by Qwen2.5-1.5B (via `llama.cpp`) and a normalized SQLite knowledge architecture. It is designed to teach all aspects of the Japanese language from JLPT N5 through N1 and beyond across 12 distinct knowledge domains.

---

## 🌟 Key Features

- **12 Comprehensive Knowledge Domains:**
  1. Grammar (文法)
  2. Vocabulary (語彙)
  3. Kanji & Orthography (漢字)
  4. Assessment & Test Prep (試験)
  5. Pragmatics & Honorifics (語用論)
  6. Linguistics & Phonology (言語学)
  7. Culture & Etiquette (文化)
  8. Modern & Net Slang (現代語)
  9. Professional Business Japanese (ビジネス)
  10. Regional Dialects (方言)
  11. Historical & Classical Japanese (古典)
  12. Literature & Poetics (文学)

- **Hierarchical Retrieval & Normalization Pipeline:**
  - Multi-key preprocessing with automated character normalization (Katakana-to-Hiragana folding, full-width/half-width ASCII conversion, and punctuation stripping).
  - Robust SQLite-backed relational schema with version tracking triggers and record-level provenance (`provenance` table).
  - Automated RAG context injection for every user interaction, ensuring factual grounding and zero-hallucination teaching.

- **Offline-First Architecture:**
  - Designed for local execution using `llama.cpp` (`llama-server`) and lightweight Python backend services (`http.server`).

---

## 📂 Project Structure

```text
AKARI-0.5B/
├── backend/            # FastAPI / http.server backend, DB access layer, persona configuration
├── frontend/           # Web UI (HTML, CSS, JavaScript)
├── data/               # SQLite database (akari.db), conversation history, unbacked query logs
├── docs/               # Architecture blueprints, evaluation plans, data sources & schemas
├── scripts/            # Database seeders, migration tools, and verification test suites
├── models/             # GGUF model weights (akari.gguf)
└── bin/                # llama.cpp binaries and runtime libraries
```

---

## 🚀 Getting Started

1. **Prerequisites:**
   - Python 3.10+
   - `llama.cpp` compatible environment (binaries included in `bin/`)

2. **Initialize Database & Seed Comprehensive Corpus:**
   ```bash
   python scripts/seed_comprehensive_db.py
   ```

3. **Run Verification Test Suite:**
   ```bash
   python scripts/test_comprehensive_verification.py
   ```

4. **Start Backend Server:**
   ```bash
   python backend/server.py
   ```

---

## 📜 License

Distributed under the CC BY-SA 4.0 License. See individual dataset provenance records in the database for upstream attribution (JMdict, KANJIDIC2, Tatoeba, etc.).
