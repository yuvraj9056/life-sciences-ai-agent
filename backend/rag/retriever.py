import os

from dotenv import load_dotenv

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

from backend.rag.embedding_service import EmbeddingService

load_dotenv()


class Retriever:

    def __init__(self):

        self.embedding_service = EmbeddingService()

        endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        api_key = os.getenv("AZURE_SEARCH_API_KEY")
        index_name = os.getenv("AZURE_SEARCH_INDEX")

        self.search_client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(api_key)
        )

    def vector_search(self, query_embedding, top_k=5):

        vector_query = VectorizedQuery(
            vector=query_embedding,
            k_nearest_neighbors=top_k,
            fields="contentVector"
        )

        results = self.search_client.search(
            search_text=None,
            vector_queries=[vector_query],
            select=["content", "source", "page"],
            top=top_k
        )

        documents = []

        for result in results:

            documents.append(
                {
                    "content": result["content"],
                    "source": result["source"],
                    "page": result["page"],
                    "score": result["@search.score"]
                }
            )

        return documents

    def retrieve(self, question, top_k=5):

        query_embedding = self.embedding_service.embed_text(question)

        return self.vector_search(
            query_embedding=query_embedding,
            top_k=top_k
        )