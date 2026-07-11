from backend.rag.rag_agent import RAGAgent

agent = RAGAgent()

result = agent.answer(
    "What are the symptoms of diabetes?"
)

print("\nAnswer:\n")
print(result["answer"])

print("\nSources:\n")

for source in result["sources"]:
    print(source)