from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    kb_url: str = Field(..., alias="KB_URL")
    llm_provider:str = Field(default="openai", alias="LLM_PROVIDER")
    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")
    llm_base_url: str = Field(default="https://api.openai.com/v1", alias="LLM_BASE_URL")
    llm_api_key: str = Field(..., alias="LLM_API_KEY")
    memory_store: str | None = Field(default=None, alias="MEMORY_STORE")
    memory_max_turns: int = Field(default=4, alias="MEMORY_MAX_TURNS")
    memory_ttl_seconds: int = Field(default=900, alias="MEMORY_TTL_SECONDS")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
@lru_cache
def get_settings() -> Settings:
    return Settings()