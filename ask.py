"""Step 3: answer questions using retrieved chunks, with citations."""
import os

import chromadb
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

DB_DIR = "chroma_db"
COLLECTION = "course_notes"
MODEL = "claude-sonnet-5-5"
TOP_K = 5

SYSTEM = (
    "You are a study assistant. Answer the question using ONLY the numbered "
    "sources provided. Cite sources inline like [Chapter 1.pdf, p.3]. "
    "If the sources do not contain the answer, say "
    "\"I can't find that in the course materials.\" Do not use outside knowledge."
)

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
collection = chromadb.PersistentClient(path=DB_DIR).get_collection(COLLECTION)


def retrieve(question, k=TOP_K):
    res = collection.query(query_texts=[question], n_results=k)
    return list(zip(res["documents"][0], res["metadatas"][0]))


def answer(question):
    hits = retrieve(question)
    context = "\n\n".join(
        f"[{i}] ({m['source']}, p.{m['page']})\n{doc}"
        for i, (doc, m) in enumerate(hits, start=1)
    )
    msg = client.messages.create(
        model=MODEL,
        max_tokens=600,
        system=SYSTEM,
        messages=[{
            "role": "user",
            "content": f"Sources:\n{context}\n\nQuestion: {question}",
        }],
    )
    return msg.content[0].text, hits


def main():
    print("Ask a question about your course notes (blank line to quit).")
    while True:
        q = input("\nQuestion: ").strip()
        if not q:
            break
        text, hits = answer(q)
        print(f"\n{text}\n")
        print("Sources retrieved:")
        for _, m in hits:
            print(f"  - {m['source']} p.{m['page']}")


if __name__ == "__main__":
    main()