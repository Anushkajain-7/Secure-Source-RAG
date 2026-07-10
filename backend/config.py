"""
SecureSource RAG — Application Configuration

Loads configuration from environment variables with sensible defaults.
All secrets must be in .env file, never in source control.
"""

from __future__ import annotations

from enum import Enum
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LLMProvider(str, Enum):
    HUGGINGFACE = "huggingface"
    OPENAI = "openai"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──
    app_name: str = "SecureSource RAG"
    app_env: Environment = Environment.DEVELOPMENT
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_secret_key: str = "change_this_to_a_random_secret_key"
    frontend_url: str = "http://localhost:3000"

    # ── PostgreSQL ──
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "securesource"
    postgres_user: str = "securesource"
    postgres_password: str = "change_me_in_production"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def sync_database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # ── Qdrant ──
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "securesource_chunks"

    # ── LLM ──
    llm_provider: LLMProvider = LLMProvider.HUGGINGFACE
    huggingface_api_key: Optional[str] = None
    huggingface_model: str = "mistralai/Mistral-7B-Instruct-v0.3"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"

    # ── Embeddings ──
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    # ── Reranker ──
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # ── Retrieval ──
    retrieval_top_k: int = 20
    rerank_top_k: int = 5
    chunk_size: int = 512
    chunk_overlap: int = 50

    # ── Security ──
    max_context_tokens: int = 4096
    audit_logging_enabled: bool = True

    # ── OCR ──
    tesseract_cmd: str = "tesseract"
    ocr_language: str = "eng"

    # ── Logging ──
    log_level: str = "INFO"
    log_format: str = "json"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
