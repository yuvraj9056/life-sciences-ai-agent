from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_openai import AzureChatOpenAI

from backend.config.settings import settings


class LLMFactory:

    @staticmethod
    def get_llm():

        provider = settings.LLM_PROVIDER

        if provider == "groq":
            return ChatGroq(
                api_key=settings.GROQ_API_KEY,
                model=settings.GROQ_MODEL,
                temperature=0
            )

        elif provider == "ollama":
            return ChatOllama(
                model=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_BASE_URL,
                temperature=0
            )

        elif provider == "azure":
            return AzureChatOpenAI(
                api_key=settings.AZURE_OPENAI_API_KEY,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                deployment_name=settings.AZURE_OPENAI_DEPLOYMENT,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                temperature=0
            )

        else:
            raise ValueError(f"Unsupported provider: {provider}")