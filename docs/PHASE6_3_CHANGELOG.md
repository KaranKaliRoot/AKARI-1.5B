# PHASE 6.3 & 6.3.1: Architecture Corrections Changelog

This document tracks the final corrections made to Phase 6 documentation to improve architectural consistency, schema integrity, and retrieval precision.

---

## 1. Evaluation Benchmark (`EVALUATION_PLAN.md`)
- **Action:** Fixed question distribution.
- **Change:** Adjusted domain distribution to total exactly 100 questions.
- **Scoring:** Defined full 0–5 rubric for Explanation Quality and separated Retrieval Correctness ($S_{\text{retri}}$) from Source Correctness ($S_{\text{source}}$).

## 2. Schema Completeness (`DATABASE_SCHEMA.md`)
- **Action:** Full implementation specification.
- **Change:**
    - Provided SQL definitions for specialized domain extension tables (`grammar`, `vocabulary`, `kanji`, `linguistics`, `dialects`, `assessment_questions`) and explicitly defined how the remaining 6 domains are represented through the shared generic structure (`entries` + `readings` + `senses` + `examples`).
    - Added `PRAGMA foreign_keys = ON;` mandate.
    - Reconciled schema with conceptual diagram (central `entries` anchor).

## 3. Provenance & Attribution (`DATA_SOURCES.md`, `DATABASE_SCHEMA.md`)
- **Action:** Reconciled provenance model.
- **Change:**
    - Defined inheritance rules: `readings`/`senses` inherit `entries.provenance_id`; `examples` allow direct overrides for record-level attribution (e.g., Tatoeba contributor data).
    - Added mandatory `contributor_attribution` and `license_name` fields to `examples` table.

## 4. Retrieval Precision (`RETRIEVAL_DESIGN.md`)
- **Action:** Clarified search behavior.
- **Change:**
    - Specified runtime FTS5/Tokenizer capability probe method (temporary virtual table creation).
    - Clarified that `unicode61` is a generic tokenizer, not morphological.
    - Defined multi-key search (normalized vs. original) and deterministic score-weighting logic.

## 5. Architectural Consistency (`PHASE6_ARCHITECTURE.md`)
- **Action:** Refined scope.
- **Change:** Clearly distinguished implemented (Phases 1–5), approved (Phase 6), and future (Phase 7+) work, ensuring no proposed capabilities are claimed as existing.

---

## 6. Phase 6.3.1 Implementation-Safety Corrections
- **Database Version Triggers (`DATABASE_SCHEMA.md`):** Specified complete `INSERT`, `DELETE`, and `AFTER UPDATE` triggers for child tables. Re-parenting (`OLD.entry_id <> NEW.entry_id`) explicitly increments versions for both old and new parent entries. Documented recursive safety and direct `entries` update rules.
- **Tatoeba Attribution Enforcement (`DATABASE_SCHEMA.md`, `DATA_SOURCES.md`):** Mandated ingestion layer validation to reject and quarantine any Tatoeba or volunteer-sourced record missing `provenance_id`, `license_name`, or `contributor_attribution`.
- **Retrieval Tie-Breaking (`RETRIEVAL_DESIGN.md`):** Defined deterministic tie-breaking logic using `NULLS LAST` for `vocabulary.frequency_rank` (applied only to vocabulary candidates) and `entries.id ASC` as the ultimate tie-breaker for entries without frequency data.
- **Domain Representation Clarity (`DATABASE_SCHEMA.md`, `PHASE6_ARCHITECTURE.md`):** Corrected claims to accurately distinguish the 6 domains with specialized SQL tables from the 6 domains using the shared generic entry structure.
