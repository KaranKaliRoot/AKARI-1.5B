# Advanced Japanese Concept Expansion Plan (Phase 7 Blueprint)

This document outlines the blueprint to extend the AKARI Knowledge Base across all 12 domains to cover edge cases, classical texts, colloquialisms, and specialized linguistic structures.

---

## 1. Domain Coverage Matrix & Target Expansions

| Domain | Scope & Advanced Concepts to Incorporate |
| :--- | :--- |
| **1. Classical & Historical (古典・文語)** | • Heian & Kamakura Bungo syntax (e.g., Kakari-musubi rules: ぞ, なむ, や, か $\rightarrow$ Rentaikei; こそ $\rightarrow$ Izenkei).<br>• Archaic auxiliary verbs (き, けり, つ, ぬ, たり, り, む, けむ, らむ, まじ, べし).<br>• Classical vocabulary,枕詞 (Makurakotoba), and ancient kana usage (歴史的仮名遣い). |
| **2. Regional Dialects (方言)** | • Kansai-ben (Osaka, Kyoto, Kobe subtleties: 〜はる, 〜へん, 〜やんけ).<br>• Tohoku-ben (Phonetic shifts, specialized vocabulary: 〜だべ, 〜すぺ).<br>• Kyushu-ben (Hakata, Kagoshima: 〜ばい, 〜たい, 〜ごたる, よか).<br>• Ryukyuan & Okinawa-ben lexical influences (ウチナーグチ). |
| **3. Pragmatics & Sociolinguistics (語用論・待遇表現)** | • Advanced Honorifics (Bikago 美化語, Sonkeigo 尊敬語, Kenjougo 謙譲語 I & II).<br>• Contextual speech shifts (Uchi vs. Soto, Gendered speech particles: わ, ぞ, ぜ, かしら).<br>• Indirect refusals, cushioning expressions (クッション言葉), and pragmatic ambiguity. |
| **4. Professional & Business (ビジネス日本語)** | • Formal business emails, honorific phone correspondence, keigo pitfalls (二重敬語).<br>• Commercial contract phrasing, formal reports, and Japanese corporate etiquette (報連相 - Hou-Ren-So). |
| **5. Linguistics & Phonology (言語学・音韻論)** | • Tokyo vs. Keihan pitch accent patterns (Atamadaka, Nakadaka, Odaka, Heiban).<br>• Sequential voicing (Rendaku 連濁) conditions and Lyman's Law.<br>• Moraic nasal assimilation and gemination (促音便, 撥音便, イ音便, ウ音便). |
| **6. Modern, Slang & Internet (現代語・ネットスラング)** | • Social media terms (草, w, 草生える, スレ, 垢, リプ, バズる).<br>• Wakamono-kotoba (Youth abbreviations: とりま, りょ, ワンチャン, 陽キャ/陰キャ).<br>• VTuber/Anime/Subculture idioms and loanword transformations. |
| **7. Literature & Poetics (日本文学・修辞法)** | • Waka & Haiku meter (5-7-5, 5-7-5-7-7), Kireji (切れ字: や, かな, けり).<br>• Classical rhetorical devices: 序詞 (Jokotoba), 掛詞 (Kakekotoba), 本歌取り (Honkadori).<br>• Modern literature prose styles (Meiji/Taisho Genbun-itchi movement to contemporary styles). |
| **8. Culture, Etiquette & Idioms (文化・慣用句・四字熟語)** | • Proverbial wisdom (ことわざ) & Four-character idioms (四字熟語: 一期一会, 以心伝心, 切磋琢磨).<br>• Seasonal customs, calendar rituals (年中行事), and etiquette rules (Gift giving, funeral/wedding customs). |
| **9. Assessment & JLPT Prep (試験対策・誤用分析)** | • Near-synonym discrimination (〜に違いない vs. 〜はずだ; 〜わけだ vs. 〜ことだ).<br>• Common learner pitfalls (Interference from English/Chinese/Korean syntax).<br>• Complex compound particles (〜をめぐって, 〜を踏まえて, 〜に即して). |
| **10. Grammar (文法体系)** | • Complete coverage of N5 through N1 compound grammar.<br>• Causative-passive permutations, passive of adversity (迷惑の受身).<br>• Conditional subtleties (ば, と, たら, なら boundary conditions). |
| **11. Vocabulary (語彙体系)** | • Polysemous verbs (かかる, かける, つく, とる, あがる).<br>• Extensive onomatopoeia/mimetic words (Giongo/Gitaigo: ぎっしり, さらさら, もやもや, わくわく). |
| **12. Kanji & Orthography (漢字・表記)** | • 2,136 Jōyō Kanji + Jinmeiyō Kanji with full radicals, historical etymology, and variants.<br>• Ateji (当て字), irregular readings (熟字訓: 今日, 昨日, 煙草, 大人). |

---

## 2. Implementation & Integration Strategy

1. **Rule-Based Normalization & Query Expansion:**
   - Expand `backend/database.py` with multi-key generation: Hiragana/Katakana folding, Romaji-to-Kana conversion, and kanji variant cross-referencing.
   - Retain fast, zero-dependency SQLite execution without heavy external dependencies.

2. **Automated Fallback & Uncertainty Attribution:**
   - When local knowledge base records are missing, clearly instruct the LLM to provide transparent pedagogical guidance while marking statements as unverified.
   - Log unbacked queries to `data/unbacked_queries.json` to automatically flag gaps in the knowledge base for subsequent database enrichment rounds.
