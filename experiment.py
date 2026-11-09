"""Compare chunk sizes by retrieval hit rate (in-memory, leaves chroma_db alone)."""
import json
from pathlib import Path

import chromadb
from pypdf import PdfReader

DATA_DIR = "data"
QUESTIONS_FILE = "eval_questions.json"
K_VALUES = [1, 3, 5]
# (words per chunk, overlap words)
CONFIGS = [(100, 20), (200, 40), (300, 60), (400, 80), (600, 120)]


def load_pages():
    pages = []
    for pdf in sorted(Path(DATA_DIR).glob("*.pdf")):
        for num, page in enumerate(PdfReader(pdf).pages, start=1):
            pages.append((pdf.name, num, (page.extract_text() or "").split()))
    return pages


def build_chunks(pages, size, overlap):
    chunks = []
    step = size - overlap
    for source, num, words in pages:
        for start in range(0, len(words), step):
            piece = words[start:start + size]
            if len(piece) >= 5:
                chunks.append({
                    "id": f"{source}:p{num}:c{len(chunks)}",
                    "source": source,
                    "page": num,
                    "text": " ".join(piece),
                })
    return chunks


def evaluate(chunks, questions, name):
    client = chromadb.EphemeralClient()
    col = client.create_collection(name)
    for i in range(0, len(chunks), 100):
        batch = chunks[i:i + 100]
        col.add(
            ids=[c["id"] for c in batch],
            documents=[c["text"] for c in batch],
            metadatas=[{"source": c["source"], "page": c["page"]} for c in batch],
        )
    hits = {k: 0 for k in K_VALUES}
    for q in questions:
        metas = col.query(query_texts=[q["question"]], n_results=max(K_VALUES))["metadatas"][0]
        for k in K_VALUES:
            if any(m["source"] == q["source"] and m["page"] in q["pages"] for m in metas[:k]):
                hits[k] += 1
    return hits


def main():
    questions = [q for q in json.loads(Path(QUESTIONS_FILE).read_text()) if q["answerable"]]
    pages = load_pages()
    n = len(questions)
    print(f"{n} answerable questions\n")
    print(f"{'chunk/overlap':<14}{'chunks':>7}{'top-1':>8}{'top-3':>8}{'top-5':>8}")
    for i, (size, overlap) in enumerate(CONFIGS):
        chunks = build_chunks(pages, size, overlap)
        hits = evaluate(chunks, questions, f"exp{i}")
        row = "".join(f"{hits[k] / n:>8.0%}" for k in K_VALUES)
        print(f"{f'{size}/{overlap}':<14}{len(chunks):>7}{row}")


if __name__ == "__main__":
    main()