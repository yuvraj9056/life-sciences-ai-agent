from backend.database.db_connection import DatabaseConnection

def get_conn():
    engine = DatabaseConnection.get_engine()
    return engine