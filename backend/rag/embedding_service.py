import os

from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings

load_dotenv()


class EmbeddingService:

    def __init__(self):

        self.embedding_model = AzureOpenAIEmbeddings(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        )

    def embed_text(self, text: str):

        return self.embedding_model.embed_query(text)

    def embed_documents(self, documents: list[str]):

        return self.embedding_model.embed_documents(documents)