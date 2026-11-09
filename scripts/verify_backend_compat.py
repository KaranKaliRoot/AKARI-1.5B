"""Verification for normalized database lookup compatibility."""
import sys
from pathlib import Path

# Add root directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from backend.database import AkariDB

db = AkariDB()

grammar_results = db.search_grammar("〜ている")
print(f"Grammar lookup results count: {len(grammar_results)}")
print(f"Sample grammar hit: {grammar_results[0] if grammar_results else None}")

vocab_results = db.search_vocabulary("食べる")
print(f"Vocabulary lookup results count: {len(vocab_results)}")
print(f"Sample vocab hit: {vocab_results[0] if vocab_results else None}")

assert len(grammar_results) > 0, "Grammar lookup failed!"
assert len(vocab_results) > 0, "Vocabulary lookup failed!"
print("COMPATIBILITY LOOKUP SUCCESSFUL!")
