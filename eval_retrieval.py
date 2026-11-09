"""Measure how often retrieval finds the correct source page."""
import json
from pathlib import Path

import chromadb

DB_DIR = "chroma_db"
COLLECTION = "course_notes"
QUESTIONS_FILE = "eval_questions.json"
K_VALUES = [1, 3, 5]

collection = chromadb.PersistentClient(path=DB_DIR).get_collection(COLLECTION)
questions = json.loads(Path(QUESTIONS_FILE).read_text())
answerable = [q for q in questions if q["answerable"]]

hits_at_k = {k: 0 for k in K_VALUES}
misses = []

for q in answerable:
    res = collection.query(query_texts=[q["question"]], n_results=max(K_VALUES))
    metas = res["metadatas"][0]
    for k in K_VALUES:
        found = any(
            m["source"] == q["source"] and m["page"] in q["pages"]
            for m in metas[:k]
        )
        if found:
            hits_at_k[k] += 1
    if not any(m["source"] == q["source"] and m["page"] in q["pages"] for m in metas[:5]):
        misses.append((q, metas[:5]))

n = len(answerable)
print(f"\nAnswerable questions: {n}")
for k in K_VALUES:
    print(f"Retrieval hit rate @ top-{k}: {hits_at_k[k]}/{n} = {hits_at_k[k] / n:.0%}")

if misses:
    print("\nMissed questions (correct page not in top 5):")
    for q, metas in misses:
        print(f"- {q['question']}")
        print(f"  expected: {q['source']} p.{q['pages']}")
        print(f"  got: {[(m['source'], m['page']) for m in metas]}")