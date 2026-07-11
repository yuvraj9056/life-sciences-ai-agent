from backend.agents.sql_agent import SQLAgent
from backend.agents.sql_validator import SQLValidator
from backend.services.sql_executor import SQLExecutor

question = "Show all diabetic patients."

agent = SQLAgent()

sql = agent.generate_sql(question)

print("\nGenerated SQL\n")
print(sql)

valid, message = SQLValidator.validate(sql)

print("\nValidation:", message)

if valid:

    executor = SQLExecutor()

    df = executor.execute(sql)

    print("\nResults\n")

    print(df.head())

    print(f"\nRows Returned: {len(df)}")

else:

    print("SQL execution blocked.")