from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_HOST: str = "localhost"
    APP_PORT: int = 8000
    CURR_CONFIG: str
    BASIC_CURR_DATE: str


settings = Settings()
