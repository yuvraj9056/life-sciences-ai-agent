from backend.config.llm_factory import LLMFactory

llm = LLMFactory.get_llm()

response = llm.invoke("Say hello in one sentence.")

print(response.content)