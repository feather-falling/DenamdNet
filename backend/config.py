"""
Backend configuration and settings.
"""

import os
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))


class Settings(BaseModel):
    app_name: str = "BRICS Smart Health & Supply Chain Resilience API"
    app_version: str = "1.0.0"
    base_dir: str = "data"
    input_dir: str = "input"
    output_dir: str = "output"
    outputs_dir: str = "outputs"
    requests_storage_file: str = "data/operational_requests.json"
    default_country: str = "all"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # PostgreSQL Database URL
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:2004@localhost:5432/brics_health"
    )
    
    # JWT Authentication
    jwt_secret: str = os.getenv("JWT_SECRET", "brics_secret_fallback_key_2026")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    # CORS Origins
    @property
    def cors_origins_list(self) -> List[str]:
        raw = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:5175")
        return [o.strip() for o in raw.split(",") if o.strip()]


settings = Settings()

