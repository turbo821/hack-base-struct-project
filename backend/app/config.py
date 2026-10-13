from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = ""
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    sqlalchemy_track_modifications: bool = False
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()