from langchain_core.output_parsers import StrOutputParser

from backend.config.llm_factory import LLMFactory
from backend.database.schema_loader import SchemaLoader
from backend.prompts.sql_prompt import SQL_SYSTEM_PROMPT


class SQLAgent:

    def __init__(self):

        self.llm = LLMFactory.get_llm()

        self.schema = SchemaLoader.get_schema()

        self.parser = StrOutputParser()

    def generate_sql(self, question: str):

        prompt = f"""
                {SQL_SYSTEM_PROMPT}

                Database Schema:
                {self.schema}

                User Question:
                {question}
                """

        chain = self.llm | self.parser

        sql = chain.invoke(prompt)

        return sql.strip()