from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    secret_key: str = '3d64e41e753e070ceee4525794d7fab1b2c6f2dc0e38495c04f2fc21c0078eace311fef8c56852dc2e46cb3433cf776c15c6d7dd2b527a4fb0e2b0906363fece'
    sqlalchemy_database_uri: str = "postgresql://{}:{}@postgresql:5432/user_service".format(
        os.getenv("USER_DATABASE_LOGIN"), os.getenv("USER_DATABASE_PASSWORD"))
    # data_service_address: str = "http://{}:{}".format(os.getenv('INTERNAL_ADDRESS'), os.getenv('DATA_SERVICE_PORT'))
    data_service_address: str = "http://{}".format(os.getenv('DATA_SERVICE_URL'))


settings = Settings()
