# Course Study Assistant (RAG)

A retrieval-augmented generation (RAG) app that answers questions about course notes and cites the source file and page for every answer. If the notes don't contain the answer, it says so instead of guessing.

Built with Python, ChromaDB, the Anthropic API, and Streamlit.

## How it works

1. **Ingest** (`ingest.py`): extracts text from PDFs page by page and splits it into overlapping word-based chunks, keeping the source file and page number with each chunk.
2. **Embed** (`embed.py`): stores the chunks in a local ChromaDB vector database using Chroma's built-in embedding model.
3. **Retrieve and answer** (`ask.py`): embeds the question, retrieves the 5 closest chunks, and sends them to Claude with instructions to answer only from those sources, cite them inline (for example `[Chapter 1.pdf, p.9]`), and refuse when the answer isn't there.
4. **Interface** (`app.py`): a Streamlit page for asking questions and expanding the retrieved source text.

## Evaluation

I built a test set of 39 questions (`eval_questions.json`) from three database lecture decks: 34 questions the notes can answer, each labeled with the correct source file and page, and 5 questions they cannot (for example, "What is the capital of France?").

| Metric | Result |
|---|---|
| Retrieval: correct page in top 1 | 28/34 (82%) |
| Retrieval: correct page in top 3 | 31/34 (91%) |
| Retrieval: correct page in top 5 | 33/34 (97%) |
| Answers citing the correct source and page | 33/34 (97%) |
| Correct refusals on out-of-scope questions | 5/5 (100%) |

**Chunk-size experiment** (`experiment.py`): I compared chunk sizes of 100, 200, 300, 400, and 600 words. Sizes of 200 words and above gave identical results, because most slides are shorter than 200 words, so each slide is already a single chunk. The 100-word setting was within one question of the others at every cutoff. I kept the 200-word default.

**Limitations**
- The test set is small (34 answerable questions), so one question is about 3 percentage points.
- The questions were written from the slides by me, not by independent users.
- "Correct citation" checks that the answer cites an expected file and page. It does not grade the written answer for accuracy; I spot-checked answers by hand.
- The one miss ("What are the main goals of normalization?") comes from retrieval: the slide is titled "Objectives of Normalization," and the wording difference pulled in other pages.

## Setup

Requires Python 3.12 (newer versions may not yet be supported by some dependencies, such as numpy).

```bash
git clone <your-repo-url>
cd course-rag
python -m venv .venv
.venv\Scripts\activate        # macOS/Linux: source .venv/bin/activate
pip install pypdf chromadb anthropic python-dotenv streamlit
```

Create a `.env` file in the project root with your API key:

```
ANTHROPIC_API_KEY=your-key-here
```

Add your own PDFs to a `data/` folder. Course materials are not included in this repo.

## Usage

```bash
python ingest.py        # PDFs -> chunks.json
python embed.py         # chunks -> ChromaDB
python ask.py           # ask questions in the terminal
streamlit run app.py    # or use the web interface
```

To run the evaluations (they use your own `eval_questions.json` with the format below):

```bash
python eval_retrieval.py   # retrieval hit rate at top-1/3/5
python eval_answers.py     # citation accuracy and refusals (calls the API)
python experiment.py       # compare chunk sizes
```

Test question format:

```json
{
  "question": "What is a foreign key?",
  "source": "Chapter 2.2.pdf",
  "pages": [20],
  "answerable": true
}
```

Use `"source": null`, `"pages": []`, and `"answerable": false` for questions the notes should not be able to answer.

## Project structure

```
ingest.py            Extract and chunk PDFs
embed.py             Build the vector database
ask.py               Retrieval + answer generation
app.py               Streamlit interface
eval_questions.json  Test questions
eval_retrieval.py    Retrieval evaluation
eval_answers.py      End-to-end answer evaluation
experiment.py        Chunk-size comparison
```

