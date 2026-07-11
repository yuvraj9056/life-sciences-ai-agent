import urllib.parse

from sqlalchemy import create_engine, text
from backend.config.settings import settings


class DatabaseConnection:

    @staticmethod
    def get_engine():
        connection_string = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={settings.AZURE_SQL_SERVER};"
            f"DATABASE={settings.AZURE_SQL_DATABASE};"
            f"UID={settings.AZURE_SQL_USERNAME};"
            f"PWD={settings.AZURE_SQL_PASSWORD};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
            f"Connection Timeout=30;"
            f"LoginTimeout=30;"
        )

        connection_url = (
            "mssql+pyodbc:///?odbc_connect="
            + urllib.parse.quote_plus(connection_string)
        )

        engine = create_engine(
            connection_url,
            pool_pre_ping=True,
            fast_executemany=True,
            connect_args={"timeout": 30},
        )

        return engine

    @staticmethod
    def test_connection():
        try:
            engine = DatabaseConnection.get_engine()

            with engine.connect() as conn:
                result = conn.execute(text("SELECT @@VERSION"))
                print("Connected Successfully!")
                print(result.scalar())

        except Exception as e:
            print(f"Connection Failed: {e}")