"""Step 1: read PDFs and split them into overlapping chunks with source info."""
import json
import sys
from pathlib import Path

from pypdf import PdfReader

CHUNK_WORDS = 200   # words per chunk
OVERLAP_WORDS = 40  # words shared between neighboring chunks


def chunk_words(words, size, overlap):
    step = size - overlap
    for start in range(0, len(words), step):
        piece = words[start:start + size]
        if piece:
            yield " ".join(piece)


def ingest_pdf(path):
    chunks = []
    reader = PdfReader(path)
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        words = text.split()
        for piece in chunk_words(words, CHUNK_WORDS, OVERLAP_WORDS):
            chunks.append({
                "id": f"{path.name}:p{page_num}:c{len(chunks)}",
                "source": path.name,
                "page": page_num,
                "text": piece,
            })
    return chunks


def main(data_dir="data", out_file="chunks.json"):
    all_chunks = []
    for pdf in sorted(Path(data_dir).glob("*.pdf")):
        found = ingest_pdf(pdf)
        print(f"{pdf.name}: {len(found)} chunks")
        all_chunks.extend(found)

    if not all_chunks:
        sys.exit("No text found. Add PDFs to data/ (scanned images need OCR).")

    Path(out_file).write_text(json.dumps(all_chunks, indent=2))
    print(f"Wrote {len(all_chunks)} chunks to {out_file}")


if __name__ == "__main__":
    main()