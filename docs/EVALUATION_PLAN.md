# AKARI Knowledge Base: Accuracy and Evaluation Plan (Phase 6.3)

AKARI's intelligence quality is evaluated using a 100-question multi-domain benchmark that separates retrieval precision from explanation generation and source accuracy.

---

## 1. Multi-Domain Coverage (Exact 100-Question Milestone)

The benchmark comprises exactly 100 expert-reviewed questions distributed across all 12 AKARI Knowledge Domains and JLPT levels (N5–N1).

| Domain | Question Count | Target Focus |
| :--- | :---: | :--- |
| **1. Grammar (文法)** | 15 | Basic to advanced sentence structures, formation rules, particles |
| **2. Vocabulary (語彙)** | 15 | Everyday words, idiomatic expressions, nuanced synonyms |
| **3. Kanji (漢字)** | 15 | Radical analysis, stroke count, on/kun readings, compounds |
| **4. Assessment & Test Prep (試験)** | 10 | JLPT-style diagnostic questions, error identification |
| **5. Pragmatics (語用論)** | 10 | Keigo (Sonkeigo, Kenjougo, Teineigo), social context, gendered speech |
| **6. Linguistics (言語学)** | 7 | Pitch accent patterns, mora timing, phonological shifts |
| **7. Culture & Etiquette (文化)** | 5 | Social etiquette, cultural idiomatic references |
| **8. Modern & Net Slang (現代語)** | 5 | Internet expressions, youth slang, contractions |
| **9. Professional Japanese (ビジネス)** | 5 | Business email formatting, formal office correspondence |
| **10. Regional Dialects (方言)** | 5 | Kansai-ben, Tohoku-ben, Kyushu-ben grammar/vocab variations |
| **11. Historical Japanese (古典)** | 4 | Bungo grammar, classical auxiliary verbs, ancient kana |
| **12. Literature (文学)** | 4 | Poetic structures (Haiku/Tanka), rhetorical tropes in prose |
| **TOTAL** | **100** | **Exact 100-Question Baseline Benchmark** |

---

## 2. Benchmark Case Schema

Each benchmark case is structured as a JSON object with explicit fields for three-part scoring:

```json
{
  "id": "BENCH_N2_GRAM_042",
  "domain": "grammar",
  "jlpt_level": "N2",
  "query": "〜に違いない と 〜はずだ の違いは何ですか？",
  "expected_entry_ids": [104, 208],
  "expected_answer": "〜に違いない shows strong subjective certainty based on intuition, while 〜はずだ represents objective expectation based on logical premise or schedule.",
  "accepted_alternatives": [
    "に違いない is conviction based on feeling; はずだ is logical deduction from evidence."
  ],
  "source_references": [
    {"table": "grammar", "id": 42, "provenance_id": 1}
  ]
}
```

---

## 3. Three-Part Scoring Framework

Evaluation evaluates three distinct sub-systems independently:

### 3.1 Retrieval Correctness Score ($S_{\text{retri}}$)
- **1.0:** Expected entry ID(s) returned in top-3 candidates.
- **0.5:** Expected entry returned, but ranked below top-3.
- **0.0:** Expected entry missed completely (RAG failure).

### 3.2 Explanation Quality Rubric (0 to 5 Scale)
- **5 (Excellent):** Flawlessly accurate explanation, correctly uses retrieved context, natural Japanese/English, zero hallucinations.
- **4 (Good):** Factually accurate and uses context correctly; minor phrasing awkwardness.
- **3 (Acceptable):** Factually correct core points, but omits important nuance or includes minor redundant text.
- **2 (Marginal):** Partial explanation containing slight factual inaccuracies or weak adherence to context.
- **1 (Poor):** Severely inaccurate explanation or significant misinterpretation of retrieved database context.
- **0 (Unacceptable / Hallucination):** Completely incorrect explanation, counterfactual grammar rules, or fake database claims.

### 3.3 Source Attribution Score ($S_{\text{source}}$)
- **1.0:** All cited database records match valid `provenance_id` sources.
- **0.5:** Partial citation or missing secondary source link.
- **0.0:** Fabricated source citations or claims of database backing when zero entries match.

---

## 4. Extensibility Guidelines
As the database expands past Phase 6:
- New test cases appended to `data/benchmarks/` maintain the same schema.
- The 100-question baseline remains a fixed regression suite, while domain-specific sub-suites scale independently.
