from typing import Callable, Dict, Any
from ..db import execute_sql
from ..settings import SETTINGS
from ..utils import tabulate_rows

def execute_sql_tool(sql: str) -> str:
    """Tool function to execute SQL and return a formatted markdown table + stats."""
    result: Dict[str, Any] = execute_sql(sql, max_rows=SETTINGS.max_rows)
    if not result["ok"]:
        return f"SQL_ERROR: {result['error']}"
    table = ""
    if result["columns"]:
        table = tabulate_rows(result["rows"], result["columns"], max_rows=SETTINGS.max_rows)
    meta = f"Rows: {result['rowcount']} | Duration: {result['duration_ms']} ms"
    return f"{meta}\n\n{table}"
