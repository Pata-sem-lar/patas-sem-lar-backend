from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str
    database_url_test: str
    jwt_secret: str
    jwt_algorithm: str
    jwt_expiration_minutes: int


settings = Settings()  # type: ignore[call-arg]
