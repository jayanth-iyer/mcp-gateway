from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MCP_GATEWAY_",
        env_file=".env",
        extra="ignore",
    )

    host: str = "0.0.0.0"
    port: int = 8000
    audit_database_url: str = "sqlite+aiosqlite:///./data/audit.db"
    registry_path: str = "config/mcp-servers.yaml"
    log_level: str = "info"


def get_settings() -> Settings:
    return Settings()
