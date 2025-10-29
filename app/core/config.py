from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=ROOT_DIR / ".env")


class GlobalConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BACKEND_GC_")

    title: str
    version: str = "1.0.0"
    description: str
    openapi_prefix: str
    api_prefix: str = ""
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    port: int
    host: str


class DatabasePostgresqlConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BACKEND_DB_PSQL_")

    host: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None

    def get_database_url(self) -> str:
        if self.url:
            # Asegurar que siempre use asyncpg como driver
            db_url = self.url
            if db_url.startswith("postgresql://"):
                db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif "+" not in db_url and db_url.startswith("postgresql"):
                db_url = db_url.replace("postgresql", "postgresql+asyncpg", 1)
            return db_url
        # Si no hay URL completa, construimos desde componentes individuales
        if not all([self.host, self.port, self.user, self.password, self.name]):
            raise ValueError(
                "Either 'url' must be provided or all of 'host', 'port', 'user', 'password', and 'name'"
            )
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class SecurityConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BACKEND_SECURITY_")

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int = 30


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BACKEND_APP_")

    environment: str
    debug: bool = False


global_config = GlobalConfig()
db_postgresql_config = DatabasePostgresqlConfig()
security_config = SecurityConfig()
app_config = AppConfig()


class Settings:
    def __init__(self):
        self.global_config = global_config
        self.db_postgresql_config = db_postgresql_config
        self.security_config = security_config
        self.app_config = app_config

    @property
    def database_postgresql_url(self) -> str:
        return self.db_postgresql_config.get_database_url()

    @property
    def project_name(self) -> str:
        return self.global_config.title

    @property
    def version(self) -> str:
        return self.global_config.version


settings = Settings()
