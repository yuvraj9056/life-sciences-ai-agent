from backend.agents.sql_validator import SQLValidator

queries = [
    "SELECT * FROM patients",
    "WITH CTE AS (SELECT * FROM patients) SELECT * FROM CTE",
    "DROP TABLE patients",
    "DELETE FROM patients",
    "UPDATE patients SET FIRST='ABC'"
]

for q in queries:

    valid, msg = SQLValidator.validate(q)

    print(q)
    print(valid, msg)
    print("-" * 50)