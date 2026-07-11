import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL")

    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

    AZURE_SQL_SERVER = os.getenv("AZURE_SQL_SERVER")
    AZURE_SQL_DATABASE = os.getenv("AZURE_SQL_DATABASE")
    AZURE_SQL_USERNAME = os.getenv("AZURE_SQL_USERNAME")
    AZURE_SQL_PASSWORD = os.getenv("AZURE_SQL_PASSWORD")
    AZURE_SQL_DRIVER = os.getenv("AZURE_SQL_DRIVER")


settings = Settings()