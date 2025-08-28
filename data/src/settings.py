import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai").lower()
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    google_api_key: str | None = os.getenv("GOOGLE_API_KEY")

    northwind_db: str = os.getenv("NORTHWIND_DB", "./data/northwind.sqlite")
    chroma_dir: str = os.getenv("CHROMA_DIR", "./storage/chroma")
    top_k: int = int(os.getenv("TOP_K", "6"))
    max_rows: int = int(os.getenv("MAX_ROWS", "50"))

SETTINGS = Settings()
