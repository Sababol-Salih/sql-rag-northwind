from __future__ import annotations
import os, re
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any

# ---------------- Memory ----------------
@dataclass
class ConversationMemory:
    k: int = 5
    turns: List[Tuple[str, str]] = field(default_factory=list)

    def add_user(self, text: str):
        self.turns.append(("user", text))
        self.turns = self.turns[-2*self.k:]

    def add_assistant(self, text: str):
        self.turns.append(("assistant", text))
        self.turns = self.turns[-2*self.k:]

    def context(self) -> str:
        buf = []
        for role, content in self.turns[-2*self.k:]:
            prefix = "User:" if role == "user" else "Assistant:"
            buf.append(f"{prefix} {content}")
        return "\n".join(buf)


# ---------------- Preferences ----------------
@dataclass
class PreferenceStore:
    country_field: Optional[str] = None      # ShipCountry or Country
    date_field: Optional[str] = None         # OrderDate or ShippedDate
    metric: Optional[str] = None             # revenue | quantity | orders
    net_revenue: Optional[bool] = None       # True = net, False = gross
    top_n: Optional[int] = None
    time_granularity: Optional[str] = None   # month | quarter | year

    def to_hints(self) -> List[str]:
        hints = []
        if self.country_field:
            if self.country_field.lower().startswith("ship"):
                hints.append("Use Orders.ShipCountry as the country field.")
            else:
                hints.append("Use Customers.Country as the country field.")
        if self.date_field:
            hints.append(f"Use {self.date_field} for date filtering.")
        if self.metric:
            m = self.metric.lower()
            if m == "revenue":
                if self.net_revenue is True:
                    hints.append("Rank by net revenue: SUM(od.UnitPrice*od.Quantity*(1-od.Discount)).")
                elif self.net_revenue is False:
                    hints.append("Rank by gross revenue: SUM(od.UnitPrice*od.Quantity).")
                else:
                    hints.append("Prefer revenue for ranking unless specified.")
            elif m == "quantity":
                hints.append("Rank by total quantity sold.")
            elif m == "orders":
                hints.append("Rank by number of orders.")
        if self.top_n:
            hints.append(f"Use LIMIT {self.top_n}.")
        if self.time_granularity:
            hints.append(f"Aggregate by {self.time_granularity}.")
        return hints

    def integrate_answer(self, answer: str):
        a = answer.lower()
        if "ship" in a and "country" in a: self.country_field = "ShipCountry"
        elif "customer" in a and "country" in a: self.country_field = "Country"
        if "orderdate" in a: self.date_field = "OrderDate"
        if "shippeddate" in a or "ship date" in a: self.date_field = "ShippedDate"
        if "revenue" in a:
            self.metric = "revenue"
            if "net" in a or "discount" in a: self.net_revenue = True
            if "gross" in a: self.net_revenue = False
        if "quantity" in a: self.metric = "quantity"
        if "orders" in a or "order count" in a: self.metric = "orders"
        m = re.search(r"top\s*(\d+)", a)
        if m: self.top_n = int(m.group(1))
        if "month" in a: self.time_granularity = "month"
        elif any(q in a for q in ["quarter","q1","q2","q3","q4"]): self.time_granularity = "quarter"
        elif "year" in a: self.time_granularity = "year"


# ---------------- Ambiguity Detector ----------------
class AmbiguityDetector:
    def detect(self, text: str, prefs: PreferenceStore) -> List[str]:
        issues = []
        t = text.lower()
        if "country" in t and ("order" in t or "ship" in t) and not prefs.country_field:
            issues.append("country_field_choice")
        if any(w in t for w in ["quarter","q1","q2","q3","q4","month","year"]) and not re.search(r"\b20\d{2}\b", t):
            issues.append("missing_year")
        if "date" in t and not prefs.date_field:
            issues.append("date_field_choice")
        if re.search(r"\btop\b(?!\s*\d+)", t) and not prefs.top_n:
            issues.append("missing_top_n")
        if ("best" in t or "top" in t) and not any(k in t for k in ["revenue","quantity","orders","sales"]) and not prefs.metric:
            issues.append("missing_metric")
        if "revenue" in t and prefs.net_revenue is None and not any(x in t for x in ["discount","net","gross"]):
            issues.append("net_vs_gross")
        if "region" in t or "market" in t:
            issues.append("region_vs_country")
        return issues

    def clarifying_questions(self, issues: List[str]) -> List[str]:
        qs = []
        if "country_field_choice" in issues:
            qs.append("Do you want shipping destination (Orders.ShipCountry) or the customer’s country (Customers.Country)?")
        if "missing_year" in issues:
            qs.append("Which year should I use? (e.g., 2023 or 2024)")
        if "date_field_choice" in issues:
            qs.append("Should I filter by OrderDate or ShippedDate?")
        if "missing_top_n" in issues:
            qs.append("How many should I list? (Top 5, Top 10?)")
        if "missing_metric" in issues:
            qs.append("Rank by revenue, quantity, or number of orders?")
        if "net_vs_gross" in issues:
            qs.append("Revenue: net (after discount) or gross (before discount)?")
        if "region_vs_country" in issues:
            qs.append("When you say region/market, do you mean countries or a regional grouping?")
        return qs


# ---------------- Error Normalizer ----------------
def normalize_error(err: Exception | str) -> str:
    msg = str(err).lower()
    if "no such column" in msg: return "That column doesn’t exist. I’ll re-check the schema."
    if "ambiguous column" in msg: return "Ambiguous column — I’ll qualify with table aliases."
    if "syntax error" in msg: return "The SQL had a syntax issue — I’ll fix it."
    if "timeout" in msg: return "Query took too long — I can add filters or a LIMIT."
    return "Something went wrong executing the query."


# ---------------- Conversation Manager ----------------
@dataclass
class ConversationManager:
    memory: ConversationMemory = field(default_factory=lambda: ConversationMemory(k=int(os.getenv("MEMORY_K","5"))))
    prefs: PreferenceStore = field(default_factory=PreferenceStore)
    detector: AmbiguityDetector = field(default_factory=AmbiguityDetector)

    def next_action(self, user_text: str) -> Dict[str, Any]:
        self.memory.add_user(user_text)
        self.prefs.integrate_answer(user_text)
        issues = self.detector.detect(user_text, self.prefs)
        if issues:
            qs = self.detector.clarifying_questions(issues)
            reply = "Clarification needed:\n- " + "\n- ".join(qs)
            self.memory.add_assistant(reply)
            return {"need_clarification": True, "questions": qs, "assistant_reply": reply}
        context = self.memory.context()
        prefs = "\n".join(self.prefs.to_hints()) or "None"
        return {"need_clarification": False, "context": context, "preference_hints": prefs}
