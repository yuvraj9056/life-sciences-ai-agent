from backend.models.planner_models import PlannerResponse


response = PlannerResponse(
    agents=["sql", "rag"],
    reason="Need SQL data and document retrieval."
)

print(response)