from typing import Literal

from pydantic import root_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST", "PROD"]
    LOG_LEVEL: Literal["INFO", "DEBAG"]
    DSN: str

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    TEST_DB_HOST: str
    TEST_DB_PORT: int
    TEST_DB_USER: str
    TEST_DB_PASS: str
    TEST_DB_NAME: str

    JWT_KEY: str
    JWT_ALG: str

    CELERY_NAME: str

    REDIS_HOST: str
    REDIS_PORT: str

    SMTP_HOST: str
    SMTP_PORT: str
    SMTP_USER: str
    SMTP_PASS: str

    @root_validator(skip_on_failure=True)
    def get_database_url(cls, values):
        mode = values["MODE"]
        if mode == "DEV":
            values[
                "DEV_DATABASE_URL"
            ] = f"postgresql+asyncpg://{values['DB_USER']}:{values['DB_PASS']}@{values['DB_HOST']}:{values['DB_PORT']}/{values['DB_NAME']}"
        elif mode == "TEST":
            values[
                "TEST_DATABASE_URL"
            ] = f"postgresql+asyncpg://{values['TEST_DB_USER']}:{values['TEST_DB_PASS']}@{values['TEST_DB_HOST']}:{values['TEST_DB_PORT']}/{values['TEST_DB_NAME']}"
        else:
            # когда появится prod версия добавить
            values[
                "PROD_DATABASE_URL"
            ] = f"postgresql+asyncpg://{values['DB_USER']}:{values['DB_PASS']}@{values['DB_HOST']}:{values['DB_PORT']}/{values['DB_NAME']}"
        return values

    class Config:
        env_file = ".env"


settings = Settings()
