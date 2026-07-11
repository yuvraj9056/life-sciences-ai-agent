from backend.agents.planner_agent import PlannerAgent

planner = PlannerAgent()

print(
    planner.route(
        "How many diabetic patients are there?"
    )
)

print(
    planner.route(
        "What are symptoms of diabetes?"
    )
)