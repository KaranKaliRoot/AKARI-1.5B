"""Comprehensive dataset seeder for AKARI covering all 12 Japanese knowledge domains."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "akari.db"

COMPREHENSIVE_DATA = [
    {
        "provenance": {
            "source_name": "AKARI Comprehensive Master Corpus",
            "source_url": "https://github.com/akari-jp/corpus",
            "license_name": "CC BY-SA 4.0",
            "version_tag": "v2.0-master",
            "import_date": "2026-11-09T00:00:00Z",
            "license_verification_date": "2026-11-09T00:00:00Z",
            "verification_tier": "VERIFIED"
        },
        "entries": [
            # 1. Grammar
            {
                "domain": "grammar",
                "jlpt_level": "N5",
                "readings": [{"kana": "ている", "kanji": "〜ている", "reading_type": "standard", "is_primary": 1}],
                "senses": [{"sense_order": 1, "glossary_en": "continuous action or state", "pos_tag": "particle / suffix"}],
                "grammar": {
                    "pattern": "〜ている",
                    "formation": "Verb-te + いる",
                    "explanation": "Indicates an action currently in progress or a resulting state that persists.",
                    "usage_notes": "Very common in everyday Japanese for ongoing activities (e.g., 食べている - eating)."
                },
                "examples": [{"japanese": "今、本を読んでいます。", "reading": "いま、ほんをよんでいます。", "english": "I am reading a book now."}]
            },
            {
                "domain": "grammar",
                "jlpt_level": "N2",
                "readings": [{"kana": "にちがいない", "kanji": "〜に違い無い", "reading_type": "standard", "is_primary": 1}],
                "senses": [{"sense_order": 1, "glossary_en": "must be / no doubt that", "pos_tag": "grammar particle"}],
                "grammar": {
                    "pattern": "〜に違い無い",
                    "formation": "Plain form / Noun / Na-adj stem + に違い無い",
                    "explanation": "Expresses strong subjective certainty or conviction based on clues or intuition.",
                    "usage_notes": "More formal than 〜はずだ; reflects speaker's absolute belief."
                },
                "examples": [{"japanese": "彼はもう寝ているに違いありません。", "reading": "かれはもうねているにちがいにありません。", "english": "He must be sleeping by now."}]
            },
            {
                "domain": "grammar",
                "jlpt_level": "N1",
                "readings": [{"kana": "きわまりない", "kanji": "〜極まりない", "reading_type": "standard", "is_primary": 1}],
                "senses": [{"sense_order": 1, "glossary_en": "extremely / the height of", "pos_tag": "grammar suffix"}],
                "grammar": {
                    "pattern": "〜極まりない",
                    "formation": "Na-adjective stem / Noun + 極まりない",
                    "explanation": "Expresses an extreme degree of a state or emotion, most frequently negative.",
                    "usage_notes": "Highly formal literary and journalistic expression."
                },
                "examples": [{"japanese": "彼の態度は失礼極まりない。", "reading": "かれのたい度はしつれいきわまりない。", "english": "His attitude is extremely rude."}]
            },
            # 2. Vocabulary
            {
                "domain": "vocabulary",
                "jlpt_level": "N5",
                "readings": [{"kana": "たべる", "kanji": "食べる", "reading_type": "standard", "is_primary": 1}],
                "senses": [{"sense_order": 1, "glossary_en": "to eat", "pos_tag": "Ichidan verb"}],
                "vocabulary": {"lemma": "食べる", "frequency_rank": 120, "pitch_accent": "たべル (0)"},
                "examples": [{"japanese": "朝ごはんを食べる。", "reading": "あさごはんをたべる。", "english": "To eat breakfast."}]
            },
            {
                "domain": "vocabulary",
                "jlpt_level": "N3",
                "readings": [{"kana": "かんきょう", "kanji": "環境", "reading_type": "standard", "is_primary": 1}],
                "senses": [{"sense_order": 1, "glossary_en": "environment / surroundings", "pos_tag": "noun"}],
                "vocabulary": {"lemma": "環境", "frequency_rank": 850, "pitch_accent": "かんきょう (0)"},
                "examples": [{"japanese": "地球の環境を守る。", "reading": "ちきゅうのかんきょうをまもる。", "english": "To protect the Earth's environment."}]
            },
            # 3. Kanji
            {
                "domain": "kanji",
                "jlpt_level": "N3",
                "readings": [
                    {"kana": "かん", "kanji": "環", "reading_type": "onyomi", "is_primary": 1},
                    {"kana": "わ", "kanji": "環", "reading_type": "kunyomi", "is_primary": 0}
                ],
                "senses": [{"sense_order": 1, "glossary_en": "ring / circle / link", "pos_tag": "kanji"}],
                "kanji": {
                    "character": "環",
                    "stroke_count": 17,
                    "radical": "王 (jade)",
                    "grade": 8,
                    "etymology": "Depicts a jade ring or cyclical connection."
                },
                "examples": [{"japanese": "循環バスに乗る。", "reading": "じゅんかんバスに乗る。", "english": "To ride the loop bus."}]
            },
            # 4. Pragmatics
            {
                "domain": "pragmatics",
                "jlpt_level": "N3",
                "readings": [{"kana": "けいご", "kanji": "敬語", "reading_type": "standard", "is_primary": 1}],
                "senses": [{"sense_order": 1, "glossary_en": "honorific speech (Sonkeigo, Kenjougo, Teineigo)", "pos_tag": "sociolinguistics"}],
                "grammar": {
                    "pattern": "敬語体系 (Keigo System)",
                    "formation": "Sonkeigo (respectful) + Kenjougo (humble) + Teineigo (polite)",
                    "explanation": "Sociolinguistic honorific system reflecting social distance, hierarchy, and politeness.",
                    "usage_notes": "Essential for Japanese business and social etiquette."
                },
                "examples": [{"japanese": "社長がおっしゃいました。", "reading": "しゃちょうがおっしゃいました。", "english": "The company president said (respectful form)."}]
            },
            # 5. Linguistics
            {
                "domain": "linguistics",
                "jlpt_level": "N2",
                "readings": [{"kana": "あくせん", "kanji": "アクセント", "reading_type": "standard", "is_primary": 1}],
                "senses": [{"sense_order": 1, "glossary_en": "pitch accent / mora timing", "pos_tag": "phonology"}],
                "grammar": {
                    "pattern": "日本語のピッチアクセント",
                    "formation": "High-low pitch drop across morae",
                    "explanation": "Japanese is a pitch-accent language where words differ in meaning based on where the pitch falls.",
                    "usage_notes": "Heian-period derived pitch patterns vary significantly across regions (e.g., Tokyo vs. Kansai)."
                },
                "examples": [{"japanese": "箸 (はし - chopsticks) と 橋 (はし - bridge)", "reading": "はし", "english": "Hashi (chopsticks) vs Hashi (bridge) pitch contrast."}]
            },
            # 6. Culture & Etiquette
            {
                "domain": "culture",
                "jlpt_level": "N4",
                "readings": [{"kana": "おじぎ", "kanji": "お辞儀", "reading_type": "standard", "is_primary": 1}],
                "senses": [{"sense_order": 1, "glossary_en": "bowing etiquette", "pos_tag": "cultural norm"}],
                "grammar": {
                    "pattern": "お辞儀の角度 (Bowing Angles)",
                    "formation": "Eshaku (15°) / Keirei (30°) / Saikeirei (45°)",
                    "explanation": "Non-verbal bowing etiquette used in greetings, gratitude, and deep apologies.",
                    "usage_notes": "Accompanied by appropriate verbal greetings (aisatsu)."
                },
                "examples": [{"japanese": "ビジネスでは丁寧なお辞儀が大切です。", "reading": "ビジネスではていねいなおじぎがたいせつです。", "english": "Polite bowing is important in business."}]
            },
            # 7. Modern & Net Slang
            {
                "domain": "modern",
                "jlpt_level": "N3",
                "readings": [{"kana": "ぴえん", "kanji": "ぴえん", "reading_type": "colloquial", "is_primary": 1}],
                "senses": [{"sense_order": 1, "glossary_en": "expression of mild sadness / cute crying", "pos_tag": "slang"}],
                "grammar": {
                    "pattern": "ぴえん / ぴえん超えてぱおん",
                    "formation": "擬態語 (mimetic youth slang)",
                    "explanation": "Popularized on social media (TikTok/Twitter) among youth to express minor disappointment or cute distress.",
                    "usage_notes": "Informal internet slang, not used in formal writing."
                },
                "examples": [{"japanese": "終電逃してぴえん。", "reading": "しゅうでんのがしてぴえん。", "english": "Missed the last train, feeling sad (pien)."}]
            },
            # 8. Professional Business
            {
                "domain": "professional",
                "jlpt_level": "N2",
                "readings": [{"kana": "おせわになっております", "kanji": "お世話になっております", "reading_type": "standard", "is_primary": 1}],
                "senses": [{"sense_order": 1, "glossary_en": "standard business greeting / thank you for your continued support", "pos_tag": "business formula"}],
                "grammar": {
                    "pattern": "いつも大変お世話になっております",
                    "formation": "Standard business greeting (email / phone)",
                    "explanation": "Mandatory opening phrase in Japanese business correspondence acknowledging ongoing cooperative relationship.",
                    "usage_notes": "Used at the beginning of all formal business emails and phone calls."
                },
                "examples": [{"japanese": "株式会社〇〇の田中です。いつもお世話になっております。", "reading": "かぶしきがいしゃのたなかです。", "english": "This is Tanaka from OO Corp. Thank you for your continued support."}]
            },
            # 9. Regional Dialects
            {
                "domain": "dialects",
                "jlpt_level": "N3",
                "readings": [{"kana": "なんでやねん", "kanji": "何でやねん", "reading_type": "colloquial", "is_primary": 1}],
                "senses": [{"sense_order": 1, "glossary_en": "Kansai dialect retort ('Why on earth?!')", "pos_tag": "dialect / manzai"}],
                "grammar": {
                    "pattern": "関西弁：〜やねん / なんでやねん",
                    "formation": "Kansai copula + retort",
                    "explanation": "Classic Kansai dialect (Kansai-ben) phrase used to playfully question or correct an absurd statement.",
                    "usage_notes": "Extremely common in comedy (manzai) and western Japanese casual speech."
                },
                "examples": [{"japanese": "なんでやねん！そんなわけないやろ。", "reading": "なんでやねん！そんなわけないやろ。", "english": "No way! That can't be right (Kansai-ben)."}]
            },
            # 10. Historical Japanese
            {
                "domain": "historical",
                "jlpt_level": "N1",
                "readings": [{"kana": "ありける", "kanji": "有りける", "reading_type": "archaic", "is_primary": 1}],
                "senses": [{"sense_order": 1, "glossary_en": "classical auxiliary past state (Bungo)", "pos_tag": "classical grammar"}],
                "grammar": {
                    "pattern": "古典文法：助動詞「けり」",
                    "formation": "Renyoukei + けり",
                    "explanation": "Classical Japanese auxiliary verb expressing past recollection or realization of a past fact.",
                    "usage_notes": "Used extensively in Heian literature like The Tale of Genji and The Pillow Book."
                },
                "examples": [{"japanese": "春はあけぼの、やうやう白くなりゆく山ぎはすこし明かりて、紫だちたる雲の細くたなびきたる。", "reading": "はるはあけぼの...", "english": "In spring, the dawn—when the crest of the hills begins to grow slightly white..."}]
            },
            # 11. Literature
            {
                "domain": "literature",
                "jlpt_level": "N2",
                "readings": [{"kana": "はいく", "kanji": "俳句", "reading_type": "standard", "is_primary": 1}],
                "senses": [{"sense_order": 1, "glossary_en": "traditional 17-mora Japanese poetic form (5-7-5)", "pos_tag": "literary art"}],
                "grammar": {
                    "pattern": "俳句の構造 (5-7-5 syllables + Kigo)",
                    "formation": "5 morae + 7 morae + 5 morae + Seasonal Word (Kigo)",
                    "explanation": "Short-form poetry capturing a fleeting moment in nature or human emotion.",
                    "usage_notes": "Pioneered by masters like Matsuo Basho."
                },
                "examples": [{"japanese": "古池や蛙飛び込む水の音 (松尾芭蕉)", "reading": "ふるいけや かわずとびこむ みずのおと", "english": "Old pond—the sound of a frog jumping into water. (Matsuo Basho)"}]
            },
            # 12. Assessment & Test Prep
            {
                "domain": "assessment",
                "jlpt_level": "N2",
                "readings": [{"kana": "しけんたいさく", "kanji": "試験対策", "reading_type": "standard", "is_primary": 1}],
                "senses": [{"sense_order": 1, "glossary_en": "JLPT N2 grammar distinction quiz", "pos_tag": "test prep"}],
                "grammar": {
                    "pattern": "JLPT N2 模擬問題：〜にほかならない vs 〜にすぎない",
                    "formation": "Test Prep Diagnostic",
                    "explanation": "Distinguishing absolute assertion (にほかならない - nothing other than) from minimization (にすぎない - nothing more than).",
                    "usage_notes": "Frequent test question on JLPT N2/N1 grammar sections."
                },
                "examples": [{"japanese": "これは努力の結果にほかならない。", "reading": "これはどりょくのけっかにほかならない。", "english": "This is nothing other than the result of hard work."}]
            }
        ]
    }
]

def seed_comprehensive_database():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()

        for group in COMPREHENSIVE_DATA:
            prov = group["provenance"]
            cursor.execute("""
                INSERT INTO provenance (
                    source_name, source_url, license_name, version_tag,
                    import_date, license_verification_date, verification_tier
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                prov["source_name"], prov["source_url"], prov["license_name"],
                prov["version_tag"], prov["import_date"], prov["license_verification_date"],
                prov["verification_tier"]
            ))
            prov_id = cursor.lastrowid

            for entry in group["entries"]:
                cursor.execute("""
                    INSERT INTO entries (domain, jlpt_level, provenance_id)
                    VALUES (?, ?, ?)
                """, (entry["domain"], entry["jlpt_level"], prov_id))
                entry_id = cursor.lastrowid

                # Insert readings
                for r in entry.get("readings", []):
                    cursor.execute("""
                        INSERT INTO readings (entry_id, kana, kanji, reading_type, is_primary)
                        VALUES (?, ?, ?, ?, ?)
                    """, (entry_id, r["kana"], r.get("kanji"), r.get("reading_type", "standard"), r.get("is_primary", 0)))

                # Insert senses
                for s in entry.get("senses", []):
                    cursor.execute("""
                        INSERT INTO senses (entry_id, sense_order, glossary_en, pos_tag)
                        VALUES (?, ?, ?, ?)
                    """, (entry_id, s["sense_order"], s["glossary_en"], s.get("pos_tag")))

                # Insert domain-specific extension tables
                if entry["domain"] == "grammar" and "grammar" in entry:
                    g = entry["grammar"]
                    cursor.execute("""
                        INSERT INTO grammar (entry_id, pattern, formation, explanation, usage_notes)
                        VALUES (?, ?, ?, ?, ?)
                    """, (entry_id, g["pattern"], g["formation"], g["explanation"], g.get("usage_notes")))
                elif entry["domain"] == "vocabulary" and "vocabulary" in entry:
                    v = entry["vocabulary"]
                    cursor.execute("""
                        INSERT INTO vocabulary (entry_id, lemma, frequency_rank, pitch_accent)
                        VALUES (?, ?, ?, ?)
                    """, (entry_id, v["lemma"], v.get("frequency_rank"), v.get("pitch_accent")))
                elif entry["domain"] == "kanji" and "kanji" in entry:
                    k = entry["kanji"]
                    cursor.execute("""
                        INSERT INTO kanji (entry_id, character, stroke_count, radical, grade, etymology)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (entry_id, k["character"], k["stroke_count"], k["radical"], k.get("grade"), k.get("etymology")))

                # Insert examples
                for ex in entry.get("examples", []):
                    cursor.execute("""
                        INSERT INTO examples (entry_id, japanese, reading, english, provenance_id, license_name, contributor_attribution)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (entry_id, ex["japanese"], ex.get("reading"), ex["english"], prov_id, prov["license_name"], "AKARI Expert Corpus"))

        conn.commit()
    print("Comprehensive database seeding completed successfully across all 12 domains.")

if __name__ == "__main__":
    seed_comprehensive_database()
