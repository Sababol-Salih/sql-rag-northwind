from conversation.manager import ConversationManager, normalize_error
import importlib

def _import_or_mock():
    """Try to use real agents; otherwise simple mocks."""
    try:
        nl2sql = importlib.import_module("agents.nl2sql_agent")
        sql_exec = importlib.import_module("agents.sql_executor_agent")
        gen = getattr(nl2sql, "generate_sql", None) or getattr(nl2sql, "run", None)
        exe = getattr(sql_exec, "execute_sql", None) or getattr(sql_exec, "run", None)
        if gen and exe:
            return gen, exe
    except Exception:
        pass

    # Fallback: mock functions so the demo still runs
    def gen(question, context, prefs):
        return "SELECT 1;"
    def exe(sql):
        return {"ok": True, "df": None}
    return gen, exe

def main():
    cm = ConversationManager()
    gen, exe = _import_or_mock()

    # 1) Ambiguous query -> see clarifiers
    out = cm.next_action("Top products in Q2")
    if out.get("need_clarification"):
        print(out["assistant_reply"])

    # 2) User clarifies preferences
    out = cm.next_action("Q2 2024 by revenue net after discount ShipCountry")
    step = out
    if step.get("need_clarification"):
        print(step["assistant_reply"])
        return

    context = step.get("context","")
    prefs_block = step.get("preference_hints","")
    full_context = f"{context}\n\nPreferences:\n{prefs_block or 'None'}"

    sql = gen("Q2 2024 by revenue net after discount ShipCountry", full_context, cm.prefs)
    try:
        result = exe(sql)
    except Exception as e:
        print(normalize_error(e))
        return

    print("SQL>", sql)
    if result.get("ok"):
        print("Result preview: ok")
    else:
        print(normalize_error(result.get("error","Unknown error")))

if __name__ == "__main__":
    main()
