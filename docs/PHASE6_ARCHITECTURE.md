# Phase 6: Comprehensive Japanese Knowledge Architecture

## Overview
AKARI (灯り) is an offline Japanese AI tutor designed to scale from JLPT N5 through N1. This document defines the approved architectural blueprint for a multi-domain Japanese intelligence system.

---

## 1. Architectural Status

### 1.1 Existing Implementation (Phases 1–5)
- **Database:** Preliminary starter database (`data/akari.db`) with core tables for `grammar`, `vocabulary`, `kanji`, and `examples`.
- **Retrieval:** Basic keyword-based substring matching (`LIKE %query%`) executed in `backend/database.py`.
- **Limitations:** No advanced morphological analysis, rigid keyword dependencies, schema lacks normalization for 1-to-many relationships (multiple readings/meanings).

### 1.2 Approved Phase 6 Architecture (Corrected 6.3)
- **Normalized SQLite Schema:** `entries`-anchored schema supporting 12 knowledge domains. Six domains (Grammar, Vocabulary, Kanji, Linguistics, Dialects, Assessment) utilize specialized extension tables, while the remaining six (Pragmatics, Historical, Literature, Culture, Modern, Professional) are represented through the shared generic structure (`readings`, `senses`, `examples`) with explicit versioning triggers.
- **Hierarchical Retrieval Pipeline:** 4-stage pipeline (Exact -> FTS5/Trigram -> Substring `LIKE` -> Base LLM Fallback) with character-normalized multi-key lookup.
- **Provenance & Integrity:** Mandatory record-level provenance via the `provenance` table and example-level attribution (`examples.contributor_attribution`).
- **Evaluation Plan:** Structured 100-question multi-domain benchmark with a 0-5 rubrics for Explanation Quality and Retrieval Scoring.

### 1.3 Future Implementation Work (Phase 7+)
- **Implementation:** Migration of `data/akari.db` to the new Phase 6.3 schema.
- **Data Ingestion:** Automated seeding scripts (`scripts/seed_db.py`) updated to handle normalized provenance.
- **Benchmark Execution:** Automated runs of the 100-question benchmark.
- **Morphological Parser Integration:** Empirical benchmarking of `Sudachi` or similar lightweight tokenizers (requires validation of memory constraints).
- **Confidence Calibration:** Fine-tuning of the "Uncertainty System" (Stage 4 Fallback).
