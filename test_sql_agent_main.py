from backend.agents.sql_agent_main import SQLQueryAgent

agent = SQLQueryAgent()

result = agent.run("Show all diabetic patients.")

print("\nGenerated SQL:\n")
print(result["sql"])

print("\nSuccess:", result["success"])

if result["success"]:
    print("\nRows Returned:", len(result["data"]))
    print(result["data"].head())
else:
    print("\nError:", result["error"])