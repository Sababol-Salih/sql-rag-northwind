from __future__ import annotations
import sys
from .agents.sql_executor_agent import build_sql_executor_agent
from .agents.nl2sql_agent import build_nl2sql_agent

def main():
    print("\nNorthwind Agentic RAG — CLI\nType 'exit' to quit.\n")
    sql_agent = build_sql_executor_agent()

    # Create a runner that takes a SQL string and returns Agent 1's output
    def analyst_runner(sql: str) -> str:
        # agent.run will pass the SQL into the tool via the prompt
        return sql_agent.run(sql)

    nl2sql = build_nl2sql_agent(analyst_runner)

    while True:
        try:
            q = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print() ; break
        if not q or q.lower() in {"exit", "quit"}:
            break
        try:
            # The NL2SQL agent will fetch context, generate SQL, delegate to Agent 1, and summarize.
            ans = nl2sql.run(q)
            print(f"\nAssistant:\n{ans}\n")
        except Exception as e:
            print(f"[Error] {e}")

if __name__ == "__main__":
    main()
