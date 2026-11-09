# PHASE 6.1: Architecture Corrections Changelog

This document tracks revisions made to Phase 6 documentation to improve architectural rigor, search capabilities, licensing compliance, and evaluation granularity.

---

## 1. Database Normalization (`DATABASE_SCHEMA.md`)
- **Action:** Refactored monolithic tables (`grammar`, `vocabulary`, `kanji`) into a normalized structure.
- **Change:** Implemented separate tables for `readings`, `senses`, and `examples` to handle 1-to-many relationships (e.g., multiple readings/meanings per word) while maintaining referential integrity via Foreign Keys.
- **Provenance:** Added explicit `provenance_id` to all entity-level tables to ensure every record links to source/license metadata.

## 2. Japanese Search Architecture (`RETRIEVAL_DESIGN.md`)
- **Action:** Expanded search pipeline specification.
- **Change:**
    - Defined normalization strategies (Kana/Kanji standardization).
    - Specified lightweight morphological analysis/tokenization simulation (trigram/substring indexing).
    - Outlined FTS5 strategy with explicit capability checks and fallback mechanisms to substring matching (`LIKE`).
    - Added specific support for compound word lookup via indexing strategies.

## 3. Licensing and Provenance (`DATA_SOURCES.md`)
- **Action:** Strengthened data management policies.
- **Change:**
    - Added mandatory license verification and attribution metadata fields.
    - Explicitly clarified obligations for JMdict/KANJIDIC2 (ShareAlike) and BCCWJ (restricted use).
    - Mandated provenance tracking at the *record level*, specifically for volunteer-sourced datasets like Tatoeba.

## 4. Evaluation Architecture (`EVALUATION_PLAN.md`)
- **Action:** Extended evaluation beyond JLPT levels.
- **Change:**
    - Broadened scope to cover all 12 knowledge domains.
    - Introduced structured metrics: Retrieval Score, Explanation Correctness, and Hallucination Resistance.
    - Added definition for "Accepted Alternatives" in benchmarks to account for linguistic nuance.

## 5. Unresolved Decisions
- **FTS5 Performance:** While FTS5 is the target, performance impact on 1.5B model latency needs validation during implementation.
- **UniDic Integration:** Exact versioning for UniDic is pending import; initial implementation may rely on basic dictionary data until morphological parser integration is finalized.
