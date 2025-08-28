# SQL Query Generator with Agentic RAG (Northwind)

Two-agent LangChain system that converts plain English to **SQLite SQL** using
**Agentic RAG** (Chroma vector store) and executes queries on the **Northwind**
database. Agent 2 (NL→SQL) interprets questions, retrieves schema/docs, writes
SQL, and delegates execution to Agent 1 (SQL Analyst), which runs the query and
returns clean, formatted answers.

---

## Quick Start

1) **Clone & install**
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2) **Add keys & config**
```bash
cp .env.example .env
# Edit .env with your OPENAI_API_KEY (or GOOGLE_API_KEY), model, and paths
```

3) **Place the database**
- Put `northwind.sqlite` in `./data/` and make sure `NORTHWIND_DB` in `.env` points to it.

4) **Build the RAG index**
```bash
python -m src.rag.index_builder
```

5) **Run the CLI demo**
```bash
python -m src.run_cli
```

6) **(Optional) Run the API**
```bash
uvicorn src.run_api:app --reload --port 8000
```

---

## What You Get

- **Two agents**
  - **Agent 2 – NL→SQL Generator**: retrieves schema/docs with Chroma, writes SQL, and calls Agent 1.
  - **Agent 1 – SQL Analyst**: executes SQL safely on SQLite (Northwind) and formats results.
- **Agentic RAG** via Chroma using OpenAI embeddings by default.
- **Memory**: `ConversationBufferMemory` for multi-turn refinement.
- **Self-heal**: basic loop—if a SQL error occurs, Agent 2 revises and retries (within limits).
- **FastAPI endpoint** for integration & demos.
- **Test queries** and logging.

---

## Sample Questions

- Which customers ordered the most in 2024?
- What are the top 3 selling product categories in France?
- How many suppliers are based in the UK?
- What is the total revenue in Q2 2023?
- Show top 5 countries by total sales
- Show best-selling products by quantity
- Revenue breakdown by category and quarter
- Average order value per customer
- Compare sales trends over months/years

> See `tests/test_queries.json` and `docs/sample_queries.md`.

---

## Why Agentic RAG?

- **Minimize hallucinations**: The NL→SQL agent consults an up-to-date vector
  index of the **real schema** and curated notes, so it avoids non-existent
  tables/columns.
- **Better joins/filters**: Docs include join keys and examples.
- **Explains assumptions**: Retrieved chunks are surfaced to the agent to justify choices.

---

## Project Structure

```
.
├── .env.example
├── README.md
├── requirements.txt
├── data/
│   └── northwind.sqlite           # put your DB here
├── docs/
│   ├── schema_notes.md
│   └── sample_queries.md
├── storage/
│   └── chroma/                    # generated at build
├── tests/
│   └── test_queries.json
└── src/
    ├── __init__.py
    ├── settings.py
    ├── db.py
    ├── utils.py
    ├── tools/
    │   └── sql_tools.py
    ├── rag/
    │   ├── __init__.py
    │   ├── index_builder.py
    │   └── retriever.py
    ├── agents/
    │   ├── __init__.py
    │   ├── sql_executor_agent.py
    │   └── nl2sql_agent.py
    ├── run_cli.py
    └── run_api.py
```

---

## Notes

- Default embeddings: **OpenAIEmbeddings**. For Gemini, enable the commented
  dependencies and env vars, then switch provider in `.env`.
- The system uses **SQLite dialect**. Use `strftime('%Y', Orders.OrderDate)` etc.
- The SQL executor caps rows (see `MAX_ROWS` in `.env`).

---

## Demo Video (≤2 min)

- Show CLI answering a natural-language question
- Print generated SQL
- Print top rows and a short explanation
- Mention how RAG context improved accuracy

Enjoy! 🚀
