from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    EMAIL_ADDRESS: str
    EMAIL_PASSWORD: str
    SECRET_KEY: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
