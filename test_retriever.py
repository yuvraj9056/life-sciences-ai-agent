from backend.rag.retriever import Retriever

retriever = Retriever()

question = "What are the symptoms of diabetes?"

results = retriever.retrieve(question)

print("\nRetrieved Documents\n")

for i, doc in enumerate(results, start=1):

    print("=" * 80)
    print(f"Document {i}")
    print("=" * 80)

    print(doc)
    print()