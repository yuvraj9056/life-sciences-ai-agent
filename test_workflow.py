from backend.graph.workflow import graph


# response = graph.invoke(
#     {
#         "question": "What are the symptoms of diabetes?"
#     }
# )

response = graph.invoke(
    {
        "question": "How many diabetic patients are there?"
    }
)

print("\nFinal Answer:\n")
print(response["answer"])
