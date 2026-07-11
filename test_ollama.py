# from langchain_ollama import ChatOllama
from backend.config.llm_factory import LLMFactory

# llm = ChatOllama(
#     model="qwen2.5:7b",
#     base_url="http://localhost:11434",
#     temperature=0
# )
llm = LLMFactory.get_llm()
response = llm.invoke("What is diabetes?")

print(response.content)