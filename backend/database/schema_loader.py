from sqlalchemy import text
from backend.database.db_connection import DatabaseConnection


class SchemaLoader:

    @staticmethod
    def get_schema():

        engine = DatabaseConnection.get_engine()
        schema = ""

        with engine.connect() as conn:

            # Fetch all tables first
            tables = conn.execute(text("""
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """)).fetchall()

            for table in tables:

                table_name = table[0]

                schema += f"\nTable: {table_name}\n"

                # Fetch all columns before the next iteration
                columns = conn.execute(text("""
                    SELECT COLUMN_NAME, DATA_TYPE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = :table_name
                    ORDER BY ORDINAL_POSITION
                """), {"table_name": table_name}).fetchall()

                for column_name, data_type in columns:
                    schema += f"  - {column_name} ({data_type})\n"

        return schema