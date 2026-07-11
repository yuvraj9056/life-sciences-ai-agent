import os

from dotenv import load_dotenv

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)

load_dotenv()


class AISearchService:

    def __init__(self):

        endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        api_key = os.getenv("AZURE_SEARCH_API_KEY")
        index_name = os.getenv("AZURE_SEARCH_INDEX")

        credential = AzureKeyCredential(api_key)

        self.index_name = index_name

        self.index_client = SearchIndexClient(
            endpoint=endpoint,
            credential=credential
        )

        self.search_client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=credential
        )

    def create_index(self):

        fields = [

            SimpleField(
                name="id",
                type=SearchFieldDataType.String,
                key=True
            ),

            SearchableField(
                name="content",
                type=SearchFieldDataType.String
            ),

            SearchableField(
                name="source",
                type=SearchFieldDataType.String
            ),

            SimpleField(
                name="page",
                type=SearchFieldDataType.Int32
            ),

            SearchField(
                name="contentVector",
                type=SearchFieldDataType.Collection(
                    SearchFieldDataType.Single
                ),
                searchable=True,
                vector_search_dimensions=1536,
                vector_search_profile_name="vector-profile"
            )

        ]

        vector_search = VectorSearch(

            algorithms=[
                HnswAlgorithmConfiguration(
                    name="hnsw-config"
                )
            ],

            profiles=[
                VectorSearchProfile(
                    name="vector-profile",
                    algorithm_configuration_name="hnsw-config"
                )
            ]

        )

        index = SearchIndex(
            name=self.index_name,
            fields=fields,
            vector_search=vector_search
        )

        try:

            self.index_client.create_index(index)

            print("Index created successfully.")

        except Exception as e:

            print(e)

    def upload_documents(
        self,
        chunks,
        embedding_service,
        batch_size=100
    ):

        total_chunks = len(chunks)

        print(f"\nGenerating embeddings for {total_chunks} chunks...\n")

        uploaded = 0

        for start in range(0, total_chunks, batch_size):

            batch_chunks = chunks[start:start + batch_size]

            texts = [
                chunk["content"]
                for chunk in batch_chunks
            ]

            embeddings = embedding_service.embed_documents(texts)

            documents = []

            for chunk, embedding in zip(batch_chunks, embeddings):

                documents.append(
                    {
                        "id": chunk["id"],
                        "content": chunk["content"],
                        "source": chunk["source"],
                        "page": chunk["page"],
                        "contentVector": embedding
                    }
                )

            results = self.search_client.upload_documents(
                documents=documents
            )

            success = sum(
                result.succeeded
                for result in results
            )

            uploaded += success

            print(
                f"Uploaded {uploaded}/{total_chunks} documents"
            )

        print("\n========================================")
        print("Document ingestion completed successfully.")
        print("========================================")