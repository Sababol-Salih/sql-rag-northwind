from langchain.agents import Tool, initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from ..tools.sql_tools import execute_sql_tool
from ..settings import SETTINGS

def build_sql_executor_agent():
    llm = ChatOpenAI(api_key=SETTINGS.openai_api_key, model=SETTINGS.llm_model, temperature=0)
    tools = [
        Tool(
            name="execute_sql",
            func=execute_sql_tool,
            description=(
                "Execute a valid SQLite SQL query against the Northwind database and "
                "return a compact markdown table (max 50 rows) plus basic stats. "
                "Input must be a raw SQL string."
            ),
        )
    ]
    system = (
        "You are Agent 1: SQL Analyst. "
        "You receive ONLY a SQL query string as input. "
        "Use the execute_sql tool to run it. "
        "Then present a short explanation and a compact markdown table (limit rows), "
        "including totals/aggregates if present. If the SQL fails, return the error."
    )
    agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=False, handle_parsing_errors=True)
    agent.agent.llm_chain.prompt.messages[0].prompt.template = system  # Set system prompt
    return agent
