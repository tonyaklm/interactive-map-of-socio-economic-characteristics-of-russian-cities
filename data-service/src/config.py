from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://{}:{}@postgresql:5432/data_service".format(
        os.getenv("DATA_DATABASE_LOGIN"), os.getenv("DATA_DATABASE_PASSWORD"))
    user_service_address: str = "{}".format(os.getenv('USER_SERVICE_URL'))
    data_service_address: str = "{}".format(os.getenv('DATA_SERVICE_URL'))


settings = Settings()
