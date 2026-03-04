from functools import lru_cache
from pydantic import BaseModel
from pathlib import Path
import os


class Settings(BaseModel):
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    model_text: str = os.getenv("MODEL_TEXT", "gpt-4.1-mini")
    model_cua: str = os.getenv("MODEL_CUA", "computer-use-preview")
    allowlist: list[str] = [x.strip() for x in os.getenv("ALLOWLIST", "*.webofscience.com,*.scopus.com").split(",") if x.strip()]
    download_limit: int = int(os.getenv("DOWNLOAD_LIMIT", "10"))
    schedule_cron: str = os.getenv("SCHEDULE_CRON", "0 9 * * 1")
    enable_pdf: bool = os.getenv("ENABLE_PDF", "false").lower() == "true"
    download_delay_min: int = int(os.getenv("DOWNLOAD_DELAY_MIN", "30"))
    download_delay_max: int = int(os.getenv("DOWNLOAD_DELAY_MAX", "90"))
    data_dir: Path = Path(os.getenv("DATA_DIR", "data"))


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    s.data_dir.mkdir(parents=True, exist_ok=True)
    (s.data_dir / "screenshots").mkdir(exist_ok=True)
    (s.data_dir / "exports").mkdir(exist_ok=True)
    (s.data_dir / "drafts").mkdir(exist_ok=True)
    (s.data_dir / "audit").mkdir(exist_ok=True)
    return s
