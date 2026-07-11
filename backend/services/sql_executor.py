import pandas as pd
from sqlalchemy import text

from backend.database.db_connection import DatabaseConnection


class SQLExecutor:

    def __init__(self):
        self.engine = DatabaseConnection.get_engine()

    def execute(self, sql: str) -> pd.DataFrame:

        with self.engine.connect() as conn:

            result = conn.execute(text(sql))

            df = pd.DataFrame(
                result.fetchall(),
                columns=result.keys()
            )

        return df