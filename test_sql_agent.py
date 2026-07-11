from backend.agents.sql_agent import SQLAgent

agent = SQLAgent()

question = "Show all diabetic patients."

sql = agent.generate_sql(question)

print("\nGenerated SQL:\n")
print(sql)