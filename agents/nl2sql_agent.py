from __future__ import annotations
from typing import Callable
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from ..rag.retriever import get_retriever
from ..settings import SETTINGS

def build_nl2sql_agent(sql_analyst_runner: Callable[[str], str] | None = None):
    """Build Agent 2 (NL→SQL). It retrieves schema/docs, writes SQL, and delegates to Agent 1."""
    llm = ChatOpenAI(api_key=SETTINGS.openai_api_key, model=SETTINGS.llm_model, temperature=0)

    retriever = get_retriever()

    def fetch_context_tool(question: str) -> str:
        docs = retriever.get_relevant_documents(question)
        joined = "\n---\n".join(d.page_content for d in docs)
        return joined or "(no context retrieved)"

    def ask_sql_analyst(sql: str) -> str:
        if sql_analyst_runner is None:
            return "CONFIG_ERROR: SQL analyst agent not wired."
        # Delegate to Agent 1 and return its formatted answer
        return sql_analyst_runner(sql)

    tools = [
        Tool(
            name="fetch_context",
            func=fetch_context_tool,
            description=(
                "Retrieve the most relevant schema, join keys, and examples for the user's question. "
                "Use this BEFORE writing SQL to avoid hallucinating table/column names.""
            ),
        ),
        Tool(
            name="ask_sql_analyst",
            func=ask_sql_analyst,
            description=(
                "Send a COMPLETE SQL string to the SQL Analyst (Agent 1) for execution. "
                "The input must be only the SQL query string.""
            ),
        ),
    ]

    system = (
        "You are Agent 2: NL-to-SQL Generator. You convert business questions into valid SQLite SQL "
        "for the Northwind schema. ALWAYS call fetch_context first to gather schema/notes. "
        "Then propose a precise SQL query that uses explicit joins, correct column names, and "
        "SQLite-compatible date functions. Avoid SELECT *. Add LIMIT 10 unless the user asks for full results. "
        "After you write the SQL, call ask_sql_analyst with ONLY the SQL string to execute it. "
        "If the analyst returns SQL_ERROR, refine your SQL and retry up to 2 times. "
        "Finally, summarize the result succinctly for the user and show the SQL used.""
    )

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        memory=memory,
        verbose=False,
        handle_parsing_errors=True,
    )
    agent.agent.llm_chain.prompt.messages[0].prompt.template = system
    return agent
