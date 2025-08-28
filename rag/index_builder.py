import os, sqlite3
from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
from ..settings import SETTINGS

def introspect_schema(db_path: str) -> List[str]:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    docs: List[str] = []
    # List tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [r[0] for r in cur.fetchall()]
    for t in tables:
        cur.execute(f"PRAGMA table_info('{t}')")
        cols = cur.fetchall()
        col_lines = [f"- {c[1]} ({c[2]})" for c in cols]
        docs.append(f"Table {t} columns:\n" + "\n".join(col_lines))
        # Add indexes
        cur.execute(f"PRAGMA index_list('{t}')")
        idx = cur.fetchall()
        if idx:
            docs.append(f"Indexes for {t}: " + ", ".join(i[1] for i in idx))
    con.close()
    return docs

def read_text_if_exists(path: str) -> str:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def build_index():
    os.makedirs(SETTINGS.chroma_dir, exist_ok=True)

    # Gather documents: schema introspection + curated notes + sample queries
    parts: List[str] = []
    parts.extend(introspect_schema(SETTINGS.northwind_db))

    notes = read_text_if_exists("./docs/schema_notes.md")
    if notes:
        parts.append(notes)

    samples = read_text_if_exists("./docs/sample_queries.md")
    if samples:
        parts.append(samples)

    # Convert to LangChain Documents
    docs = [Document(page_content=p) for p in parts if p.strip()]

    # Create embeddings + Chroma
    embeddings = OpenAIEmbeddings(api_key=SETTINGS.openai_api_key)
    Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory=SETTINGS.chroma_dir)
    print(f"Built Chroma index at {SETTINGS.chroma_dir} with {len(docs)} docs.")

if __name__ == "__main__":
    build_index()
