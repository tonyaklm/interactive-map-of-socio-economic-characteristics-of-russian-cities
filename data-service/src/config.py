from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://data_service:data_service@postgresql:5432/data_service"


settings = Settings()
