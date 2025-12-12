from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME = "ABSA System"
    DATABASE_URL: str = "sqlite:///./absa.db"
    SECRET_KEY: str = "09d25e094faa6ca2556c81"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
