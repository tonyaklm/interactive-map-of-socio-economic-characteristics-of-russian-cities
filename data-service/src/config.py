from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://{}:{}@postgresql:5432/data_service".format(
        os.getenv("DATA_DATABASE_LOGIN"), os.getenv("DATA_DATABASE_PASSWORD"))


settings = Settings()
