"""Evaluate full answers: correct citations and correct refusals."""
import json
import re
from pathlib import Path

from ask import answer  # reuses retrieval + LLM from ask.py

QUESTIONS_FILE = "eval_questions.json"
REFUSAL = "can't find that in the course materials"

questions = json.loads(Path(QUESTIONS_FILE).read_text())

cited_ok = refused_ok = 0
n_answerable = n_unanswerable = 0
problems = []

for i, q in enumerate(questions, start=1):
    text, _ = answer(q["question"])
    refused = REFUSAL in text.lower().replace("\u2019", "'")
    if q["answerable"]:
        n_answerable += 1
        cited_pages = {int(p) for p in re.findall(r"p\.\s*(\d+)", text)}
        good = (not refused) and q["source"] in text and bool(cited_pages & set(q["pages"]))
        cited_ok += good
        if not good:
            problems.append(("answerable", q["question"], "refused" if refused else f"cited pages {sorted(cited_pages)}"))
    else:
        n_unanswerable += 1
        refused_ok += refused
        if not refused:
            problems.append(("unanswerable", q["question"], "did not refuse"))
    print(f"{i}/{len(questions)} done")

print(f"\nCorrect citation on answerable questions: {cited_ok}/{n_answerable} = {cited_ok / n_answerable:.0%}")
print(f"Correct refusal on unanswerable questions: {refused_ok}/{n_unanswerable} = {refused_ok / n_unanswerable:.0%}")

if problems:
    print("\nProblems:")
    for kind, question, note in problems:
        print(f"- [{kind}] {question} -> {note}")