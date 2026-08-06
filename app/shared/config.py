from pathlib import Path
from typing import Literal
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)
from sqlalchemy import URL


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    llm_enabled: bool = False

    rag_exact_reuse_enabled: bool = True

    llm_provider: Literal[
        "openai",
        "ollama",
    ] = "ollama"

    llm_analysis_timeout_seconds: float = Field(
        default=120.0,
        gt=0,
    )

    llm_max_report_characters: int = Field(
        default=50_000,
        ge=1_000,
    )

    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"

    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen3:8b"
    app_name: str = "AI VPS Management"
    debug: bool = True

    postgres_host: str = "127.0.0.1"

    postgres_port: int = Field(
        default=5432,
        ge=1,
        le=65535,
    )

    postgres_db: str
    postgres_user: str
    postgres_password: str

    default_ssh_private_key_path: Path
    ssh_known_hosts_path: Path
    llm_analysis_queue_size_per_server: int = Field(
        default=100,
        ge=1,
        le=10_000,
    )
    monitor_polling_interval_seconds: float = Field(
        default=5.0,
        gt=0,
    )

    default_monitor_interval_seconds: int = Field(
        default=60,
        ge=5,
    )

    rag_vector_enabled: bool = True
    embedding_provider: Literal["ollama"] = "ollama"
    ollama_embedding_model: str = "nomic-embed-text"
    embedding_dimensions: int = Field(default=768, ge=1)
    embedding_timeout_seconds: float = Field(default=60.0, gt=0)
    rag_top_k: int = Field(default=5, ge=1, le=50)

    command_timeout_seconds: float = Field(
        default=20.0,
        gt=0,
    )

    ssh_connect_timeout_seconds: float = Field(
        default=15.0,
        gt=0,
    )

    max_concurrent_servers: int = Field(
        default=5,
        ge=1,
        le=100,
    )

    database_echo: bool = False

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()