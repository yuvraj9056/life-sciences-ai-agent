from backend.agents.sql_agent import SQLAgent
from backend.agents.sql_validator import SQLValidator
from backend.services.sql_executor import SQLExecutor


class SQLQueryAgent:

    def __init__(self):
        self.sql_agent = SQLAgent()
        self.executor = SQLExecutor()

    def run(self, question: str):

        # Step 1: Generate SQL
        sql = self.sql_agent.generate_sql(question)

        # Step 2: Validate SQL
        valid, message = SQLValidator.validate(sql)

        if not valid:
            return {
                "success": False,
                "sql": sql,
                "error": message,
                "data": None
            }

        # Step 3: Execute SQL
        df = self.executor.execute(sql)

        return {
            "success": True,
            "sql": sql,
            "error": None,
            "data": df
        }