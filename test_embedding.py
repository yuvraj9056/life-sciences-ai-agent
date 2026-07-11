from backend.rag.embedding_service import EmbeddingService

service = EmbeddingService()

embedding = service.embed_text(
    "Diabetes is a chronic disease characterized by high blood glucose levels."
)

print("Embedding Dimension:", len(embedding))

print("\nFirst 10 values:")

print(embedding[:10])