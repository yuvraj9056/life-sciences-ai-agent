from sqlalchemy import text

from backend.database.db_connection import DatabaseConnection

engine = DatabaseConnection.get_engine()

try:
    print("Attempting SQL Server connection...")

    with engine.connect() as conn:
        print("Connection established.")

        result = conn.execute(text("SELECT @@VERSION"))
        version = result.scalar()

        print("Connected successfully!")
        print("SQL Server Version:")
        print(version)

except Exception as e:
    print("Connection failed.")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Details: {e}")
    raise