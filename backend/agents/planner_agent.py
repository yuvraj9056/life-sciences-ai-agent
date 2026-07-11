from langchain_core.output_parsers import StrOutputParser

from backend.config.llm_factory import LLMFactory
from backend.prompts.planner_prompt import PLANNER_PROMPT


class PlannerAgent:

    def __init__(self):

        self.llm = LLMFactory.get_llm()

        self.parser = StrOutputParser()

    def route(self, question: str):

        prompt = f"""
        {PLANNER_PROMPT}

        User Question:
        {question}
        """

        chain = self.llm | self.parser

        route = chain.invoke(prompt)

        route = route.strip().lower()

        if "sql" in route:
            return "sql"

        return "rag"