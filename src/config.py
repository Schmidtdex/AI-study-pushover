import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv(override=True)

def _required(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Environment variable {key} is required")
    return value



@dataclass(frozen=True)
class Config:
    database_url: str
    pushover_user: str
    pushover_token: str
    groq_api_key: str
    gemini_api_key: str


config = Config(
    database_url=_required("DATABASE_URL"),
    pushover_user=_required("PUSHOVER_USER"),
    pushover_token=_required("PUSHOVER_TOKEN"),
    groq_api_key=_required("GROQ_API_KEY"),
    gemini_api_key=_required("GEMINI_API_KEY"),
)