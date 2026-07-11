from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os

load_dotenv()


class BlobReader:
    def __init__(self):
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        container_name = os.getenv("BLOB_CONTAINER_NAME")

        self.container_client = BlobServiceClient.from_connection_string(
            connection_string
        ).get_container_client(container_name)

    def list_pdfs(self):
        """Return all PDF filenames from the blob container."""
        return [
            blob.name
            for blob in self.container_client.list_blobs()
            if blob.name.lower().endswith(".pdf")
        ]

    def download_pdf(self, blob_name):
        """Download a PDF and return its bytes."""
        blob_client = self.container_client.get_blob_client(blob_name)
        return blob_client.download_blob().readall()