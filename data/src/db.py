from __future__ import annotations
import time
from typing import Any, Dict
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Result
from .settings import SETTINGS

_engine: Engine | None = None

def get_engine() -> Engine:
    global _engine
    if _engine is None:
        # sqlite: triple slash relative, four slash absolute. Use file path from env.
        url = f"sqlite:///{SETTINGS.northwind_db}"
        _engine = create_engine(url, echo=False, future=True)
    return _engine

def execute_sql(sql: str, max_rows: int | None = None) -> Dict[str, Any]:
    engine = get_engine()
    start = time.time()
    out: Dict[str, Any] = {
        "ok": True,
        "error": None,
        "rowcount": 0,
        "columns": [],
        "rows": [],
        "duration_ms": None,
    }
    try:
        with engine.connect() as conn:
            result: Result = conn.execute(text(sql))
            if result.returns_rows:
                rows = result.fetchall()
                cols = list(result.keys())
                out["columns"] = cols
                out["rowcount"] = len(rows)
                if max_rows is None:
                    max_rows = SETTINGS.max_rows
                out["rows"] = [list(r) for r in rows[:max_rows]]
            else:
                out["rowcount"] = result.rowcount or 0
    except Exception as e:
        out["ok"] = False
        out["error"] = f"{type(e).__name__}: {e}"
    finally:
        out["duration_ms"] = int((time.time() - start) * 1000)
    return out
