# AKARI Knowledge Base: Data Sources & Provenance (Phase 6.3)

AKARI maintains factual integrity through a record-level provenance system. No legal guarantees are made; all licensing information is recorded for audit.

---

## 1. Provenance Meta-Model (`provenance` Table)
Every entry record MUST map to a `provenance` record containing:
- `source_name`: Dataset identifier.
- `source_url`: URL of origin.
- `license_name`: Name (e.g., CC BY-SA 3.0).
- `license_url` / `license_text`: License details.
- `version_tag`: Exact dataset version.
- `import_date`: ISO 8601 UTC.
- `license_verification_date`: ISO 8601 UTC.
- `verification_tier`: `VERIFIED` (expert), `PEER-REVIEWED` (community), `AUTOMATED` (scripted).

---

## 2. Core Datasets & Provenance Rules

### 2.1 JMdict & KANJIDIC2
- **Origin:** [EDRDG](http://www.edrdg.org/).
- **License:** [CC BY-SA 3.0](https://www.edrdg.org/edrdg/licence.html).
- **Provenance Requirement:** Import must map these records to a `provenance` record with explicit ShareAlike license text.

### 2.2 Tatoeba (Example Sentences)
- **Origin:** [Tatoeba Project](https://tatoeba.org/).
- **License:** [CC BY 2.0 FR](https://tatoeba.org/en/terms_of_use).
- **Mandatory Attribution (Record-Level):** 
  - Each `examples` table entry MUST populate `provenance_id`, `license_name`, and `contributor_attribution` (the original Tatoeba contributor).
  - **Ingestion Validation:** The ingestion layer MUST validate these three fields. Any record missing contributor attribution or source provenance MUST fail with an explicit error and be quarantined for review. Silent acceptance of incomplete attribution is prohibited.

### 2.3 UniDic (Morphological Meta-data)
- **Origin:** [NINJAL](https://unidic.ninjal.ac.jp/).
- **Provenance Requirement:** MUST record exact UniDic version (e.g., `UniDic-v3.1.1-modern`) in `provenance.version_tag`.
- **Note:** Version/License status must be verified against release documentation prior to ingestion script execution.

### 2.4 BCCWJ (Balanced Corpus)
- **Status:** Restricted.
- **Access Rule:** BCCWJ raw text MUST NOT be redistributed. AKARI can only integrate pre-computed word frequency metrics.

---

## 3. Metadata Preservation Fields

The schema enforces provenance at two levels:

| Location | Mechanism | Usage |
| :--- | :--- | :--- |
| `entries` | `provenance_id` (FK) | Dataset-level source for grammar/vocab/kanji. |
| `examples` | `provenance_id`, `license_name`, `contributor_attribution` | Record-level override for sentence attribution. |

*Note: `readings` and `senses` tables inherit dataset provenance implicitly via their parent `entries.provenance_id` relationship.*
