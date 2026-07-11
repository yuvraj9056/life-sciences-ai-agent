import re


class SQLValidator:

    ALLOWED = ["SELECT", "WITH"]

    BLOCKED = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "TRUNCATE",
        "EXEC",
        "MERGE",
        "CREATE"
    ]

    @staticmethod
    def validate(sql: str):

        if not sql:
            return False, "Empty SQL query."

        sql = sql.strip()

        upper_sql = sql.upper()

        if not any(upper_sql.startswith(cmd) for cmd in SQLValidator.ALLOWED):
            return False, "Only SELECT queries are allowed."

        for keyword in SQLValidator.BLOCKED:
            if re.search(rf"\b{keyword}\b", upper_sql):
                return False, f"Blocked SQL keyword: {keyword}"

        return True, "Valid SQL"