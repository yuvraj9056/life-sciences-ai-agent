from langchain_core.output_parsers import StrOutputParser

from backend.config.llm_factory import LLMFactory
from backend.rag.retriever import Retriever


RAG_SYSTEM_PROMPT = """
You are an expert medical AI assistant.

Answer the user's question ONLY using the provided context.

Rules:
1. Use only the provided context.
2. Do not make up information.
3. If the answer is not present in the context, reply:
   "I could not find the answer in the provided documents."
4. Answer clearly and concisely.
5. If appropriate, present the answer as bullet points.
"""


class RAGAgent:

    def __init__(self):

        self.llm = LLMFactory.get_llm()

        self.retriever = Retriever()

        self.parser = StrOutputParser()

    def _build_context(self, documents):

        context = ""

        for i, doc in enumerate(documents, start=1):

            context += f"""
Document {i}
Source: {doc['source']}
Page: {doc['page']}

{doc['content']}

--------------------------------------------------
"""

        return context

    def answer(self, question: str):

        documents = self.retriever.retrieve(question)

        context = self._build_context(documents)

        prompt = f"""
{RAG_SYSTEM_PROMPT}

Context:
{context}

User Question:
{question}
"""

        chain = self.llm | self.parser

        answer = chain.invoke(prompt)

        return {
            "answer": answer.strip(),
            "sources": [
                {
                    "source": doc["source"],
                    "page": doc["page"]
                }
                for doc in documents
            ]
        }