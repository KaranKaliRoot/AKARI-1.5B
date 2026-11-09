# PHASE 6.2: Final Architecture Consistency Changelog

This document summarizes the comprehensive corrections and architectural alignment executed in Phase 6.2 across all AKARI knowledge architecture documents.

---

## 1. Summary of Corrections

- **`DATABASE_SCHEMA.md`:** 
  - Mapped all 12 knowledge domains to the normalized `entries` architecture via extension tables (`grammar`, `vocabulary`, `kanji`, `linguistics`, `dialects`, etc.) and shared attributes (`readings`, `senses`, `examples`).
  - Defined explicit Foreign Keys with deletion behaviors (`ON DELETE CASCADE` / `ON DELETE RESTRICT`), indexes, uniqueness constraints, and the entry versioning lifecycle.
  - Included a conceptual schema relationship diagram.
- **`RETRIEVAL_DESIGN.md`:** 
  - Clarified runtime FTS5 capability detection and tokenizer options (`trigram` vs `unicode61`).
  - Explicitly corrected the misconception that `unicode61` is a Japanese morphological tokenizer.
  - Established a 4-stage retrieval fallback hierarchy (Exact -> FTS5/Trigram -> Substring `LIKE` -> Base LLM Uncertainty Fallback).
- **`DATA_SOURCES.md`:** 
  - Strengthened provenance requirements to mandate exact version tags, source URLs, license texts, verification dates, contributor attribution (especially for Tatoeba sentences), and strict distinction between BCCWJ access vs. redistribution.
- **`EVALUATION_PLAN.md`:** 
  - Outlined initial coverage distribution across all 12 knowledge domains for the 100-question milestone.
  - Defined measurable metrics for Retrieval Correctness and Explanation Quality (0–5 rubric), alongside uncertainty calibration testing.
- **`PHASE6_ARCHITECTURE.md`:** 
  - Clearly separated Existing Implementation (Phases 1–5), Approved Phase 6 Architecture, and Future Implementation Work (Phase 7+).

---

## 2. Key Architectural Decisions & Trade-offs

1. **Zero-Dependency Matching:** To respect the 8 GB RAM limit and keep installation simple on offline systems, we avoided heavy NLP libraries (MeCab/Sudachi) in the core runtime, utilizing maximal-matching segmentation and trigrams instead.
2. **Record-Level Provenance:** Rather than assuming entire datasets share a single license, `examples` support direct record-level provenance and contributor attribution (crucial for Tatoeba).
3. **Uncertainty Fallback:** When verified records are missing, the system explicitly flags unbacked generations rather than hallucinating fake database entries.

---

## 3. Unresolved Questions & Benchmark Trade-offs

1. **FTS5 Trigram Performance:** While SQLite FTS5 with trigram is ideal for Japanese substring indexing, its performance impact on 1.5B model generation latency requires empirical benchmarking during Phase 7 implementation.
2. **UniDic Integration Complexity:** Exact licensing and dependency footprint for UniDic morphological data need further audit before ingestion scripts are finalized.
