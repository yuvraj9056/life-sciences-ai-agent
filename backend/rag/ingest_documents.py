from backend.rag.pdf_reader import PDFReader
from backend.rag.chunker import DocumentChunker
from backend.rag.embedding_service import EmbeddingService
from backend.rag.ai_search_service import AISearchService
import os

batch_size = int(
    os.getenv("EMBEDDING_BATCH_SIZE", "100")
)

PDF_FOLDER = "datasets/unstructured"


def main():

    print("=" * 60)
    print("Reading PDFs...")
    print("=" * 60)

    pdfs = PDFReader.read_folder(PDF_FOLDER)

    print(f"Loaded {len(pdfs)} PDFs")

    print("\n" + "=" * 60)
    print("Chunking documents...")
    print("=" * 60)

    chunker = DocumentChunker()

    chunks = chunker.chunk_documents(pdfs)

    print(f"Generated {len(chunks)} chunks")

    print("\n" + "=" * 60)
    print("Initializing Embedding Service...")
    print("=" * 60)

    embedding_service = EmbeddingService()

    print("Embedding service initialized")

    print("\n" + "=" * 60)
    print("Initializing Azure AI Search...")
    print("=" * 60)

    ai_search = AISearchService()

    ai_search.upload_documents(
    chunks=chunks,
    embedding_service=embedding_service,
    batch_size=batch_size
    )

    print("\n" + "=" * 60)
    print("Document ingestion completed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()