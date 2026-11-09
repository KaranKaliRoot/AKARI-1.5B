"""Phase 3 Test Suite for AKARI Backend API."""

import json
import time
import sys
import urllib.error
import urllib.request

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')

API_BASE = "http://127.0.0.1:8081/api"


def post_json(endpoint: str, data: dict, timeout: float = 120.0) -> tuple[int, dict]:
    url = f"{API_BASE}{endpoint}"
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        try:
            return e.code, json.loads(err_body)
        except Exception:
            return e.code, {"error": err_body}
    except Exception as e:
        return 500, {"error": str(e)}


def get_json(endpoint: str, timeout: float = 10.0) -> tuple[int, dict]:
    url = f"{API_BASE}{endpoint}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        try:
            return e.code, json.loads(err_body)
        except Exception:
            return e.code, {"error": err_body}
    except Exception as e:
        return 500, {"error": str(e)}


def delete_json(endpoint: str, timeout: float = 10.0) -> tuple[int, dict]:
    url = f"{API_BASE}{endpoint}"
    req = urllib.request.Request(url, method="DELETE")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        try:
            return e.code, json.loads(err_body)
        except Exception:
            return e.code, {"error": err_body}
    except Exception as e:
        return 500, {"error": str(e)}


def run_tests():
    print("=" * 60)
    print("AKARI Phase 3 Automated Test Suite")
    print("=" * 60)

    # Health Check
    status, res = get_json("/health")
    print(f"\n1. Health Check (GET /api/health): Status {status}")
    print(f"   Response: {res}")

    # Test 1: Normal English conversation
    print("\n2. Test 1: Normal English Conversation")
    status, res1 = post_json(
        "/chat",
        {
            "session_id": "test_english_session",
            "message": "Hello Akari! Can you tell me a little bit about yourself and what you like to do?",
            "max_tokens": 150,
        },
    )
    print(f"   Status {status}")
    print(f"   Session ID: {res1.get('session_id')}")
    print(f"   Akari: {res1.get('response')}")

    # Test 2: Japanese N5 conversation
    print("\n3. Test 2: Japanese N5 Conversation")
    status, res2 = post_json(
        "/chat",
        {
            "session_id": "test_n5_session",
            "mode": "teaching",
            "message": "こんにちは！私は日本語を勉強しています。N5レベルの簡単なお話をしましょう。",
            "max_tokens": 150,
        },
    )
    print(f"   Status {status}")
    print(f"   Session ID: {res2.get('session_id')}")
    print(f"   Akari: {res2.get('response')}")

    # Test 3: Japanese N3 grammar explanation
    print("\n4. Test 3: Japanese N3 Grammar Explanation")
    status, res3 = post_json(
        "/chat",
        {
            "session_id": "test_n3_grammar",
            "mode": "teaching",
            "message": "N3文法の「〜ことにしている」と「〜ことになっている」の違いを例文付きで分かりやすく教えてください。",
            "max_tokens": 250,
        },
    )
    print(f"   Status {status}")
    print(f"   Akari: {res3.get('response')}")

    # Test 4: Japanese N1-level language explanation
    print("\n5. Test 4: Japanese N1 Language Explanation")
    status, res4 = post_json(
        "/chat",
        {
            "session_id": "test_n1_grammar",
            "mode": "teaching",
            "message": "N1文法の「〜極まりない」と「〜の極み」の意味と使い分けを解説してください。",
            "max_tokens": 250,
        },
    )
    print(f"   Status {status}")
    print(f"   Akari: {res4.get('response')}")

    # Test 5: Japanese sentence correction
    print("\n6. Test 5: Japanese Sentence Correction")
    status, res5 = post_json(
        "/chat",
        {
            "session_id": "test_correction",
            "mode": "correction",
            "message": "次の文の不自然なところを直してください：「昨日友達と映画を行きました。とても面白かったでした。」",
            "max_tokens": 200,
        },
    )
    print(f"   Status {status}")
    print(f"   Akari: {res5.get('response')}")

    # Test 6: Open-ended fictional roleplay
    print("\n7. Test 6: Open-ended Fictional Roleplay")
    status, res6 = post_json(
        "/chat",
        {
            "session_id": "test_roleplay",
            "mode": "roleplay",
            "message": "【設定：東京の小さな喫茶店『あかり』。あなたは店主。雨の日の夕方】雨がひどくなってきたので、店に入って雨宿りさせてもらうよ。「すみません、温かいお茶をいただけますか？」",
            "max_tokens": 200,
        },
    )
    print(f"   Status {status}")
    print(f"   Akari: {res6.get('response')}")

    # Test 7: Multi-turn conversational continuity
    print("\n8. Test 7: Multi-turn Conversational Continuity")
    # Follow-up in test_english_session
    status, res7a = post_json(
        "/chat",
        {
            "session_id": "test_english_session",
            "message": "I mentioned my favorite hobby earlier or what I like. What was my name again, and what did we talk about?",
            "max_tokens": 150,
        },
    )
    print(f"   Follow-up Status {status}")
    print(f"   Akari: {res7a.get('response')}")

    # Test 8: Multiple independent conversation sessions
    print("\n9. Test 8: Multiple Independent Sessions & Persistence")
    status, conversations = get_json("/conversations")
    print(f"   GET /api/conversations Status {status}")
    print(f"   Session count: {len(conversations.get('conversations', []))}")
    for s in conversations.get("conversations", []):
        print(f"     - ID: {s['session_id']}, Mode: {s['mode']}, Messages: {s['message_count']}")

    # Get specific session details
    status, sess_detail = get_json("/conversations/test_english_session")
    print(f"\n   GET /api/conversations/test_english_session Status {status}")
    print(f"   Fetched message count: {len(sess_detail.get('messages', []))}")

    # Test Error Handling: Invalid JSON, Missing message, Invalid session DELETE
    print("\n10. Test 9: Error Handling")
    status, err1 = post_json("/chat", {})
    print(f"   Empty payload -> Status {status}, Error: {err1}")

    status, err2 = get_json("/conversations/non_existent_id_12345")
    print(f"   Missing session -> Status {status}, Error: {err2}")

    status, del1 = delete_json("/conversations/non_existent_id_12345")
    print(f"   Delete non-existent -> Status {status}, Error: {del1}")

    print("\n" + "=" * 60)
    print("Test Suite Execution Finished")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
