from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    sqlalchemy_track_modifications: bool = False
    postgres_user:str = "app"
    postgres_password: str = "app"
    postgres_db: str = "app"
    database_url: str = "postgresql://app:app@db:5432/app"
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
