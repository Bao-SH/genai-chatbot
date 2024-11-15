from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv()


class Settings(BaseSettings):
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_API_BASE: str
    AZURE_OPENAI_API_VERSION: str

    class Config:
        env_file = ".env"

settings = Settings()