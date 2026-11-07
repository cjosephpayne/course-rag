"""Step 2: embed chunks and store them in a local Chroma vector database."""
import json
from pathlib import Path

import chromadb

CHUNKS_FILE = "chunks.json"
DB_DIR = "chroma_db"
COLLECTION = "course_notes"
BATCH = 100


def main():
    chunks = json.loads(Path(CHUNKS_FILE).read_text())
    chunks = [c for c in chunks if len(c["text"].split()) >= 5]  # skip near-empty chunks

    client = chromadb.PersistentClient(path=DB_DIR)
    collection = client.get_or_create_collection(COLLECTION)

    for i in range(0, len(chunks), BATCH):
        batch = chunks[i:i + BATCH]
        collection.upsert(
            ids=[c["id"] for c in batch],
            documents=[c["text"] for c in batch],
            metadatas=[{"source": c["source"], "page": c["page"]} for c in batch],
        )
        print(f"Stored {min(i + BATCH, len(chunks))}/{len(chunks)}")

    print(f"Done. {collection.count()} chunks in the database.")

    # Quick test search
    query = "What is normalization?"
    results = collection.query(query_texts=[query], n_results=3)
    print(f"\nTest search: {query}")
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        print(f"- {meta['source']} page {meta['page']}: {doc[:120]}...")


if __name__ == "__main__":
    main()