from fastapi import FastAPI
from pydantic import BaseModel
from .agents.sql_executor_agent import build_sql_executor_agent
from .agents.nl2sql_agent import build_nl2sql_agent

app = FastAPI(title="Northwind Agentic RAG API")

sql_agent = build_sql_executor_agent()
def analyst_runner(sql: str) -> str:
    return sql_agent.run(sql)

nl2sql_agent = build_nl2sql_agent(analyst_runner)

class AskPayload(BaseModel):
    question: str

@app.post("/ask")
def ask(p: AskPayload):
    answer = nl2sql_agent.run(p.question)
    return {"answer": answer}
