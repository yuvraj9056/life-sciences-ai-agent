from backend.graph.workflow import build_graph

graph = build_graph()

state = {
    "query": "Show diabetic patients",
    "planner_output": {},
    "sql_result": "",
    "rag_result": "",
    "analytics_result": "",
    "final_answer": ""
}

result = graph.invoke(state)

print(result)