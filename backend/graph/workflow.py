from langgraph.graph import StateGraph, END

from backend.models.state import AgentState
from backend.utils.logger import logger

from backend.agents.planner_agent import PlannerAgent
from backend.agents.sql_agent_main import SQLQueryAgent
from backend.rag.rag_agent import RAGAgent
from backend.agents.response import ResponseAgent

# =====================================================
# Initialize Agents 
# =====================================================

planner = PlannerAgent()
sql_agent = SQLQueryAgent()
rag_agent = RAGAgent()
response_agent = ResponseAgent()

# =====================================================
# Planner Node
# =====================================================

def planner_node(state: AgentState):

    question = state["question"]

    route = planner.route(question)

    print(f"\nPlanner Selected: {route}")

    return {
        "route": route
    }


# =====================================================
# SQL Node
# =====================================================

def sql_node(state: AgentState):

    question = state["question"]

    print("\nExecuting SQL Agent...\n")

    result = sql_agent.run(question)

    #loging intermediate results
    logger.info("===== SQL AGENT =====")
    logger.info("Question: %s", question)
    logger.info("Generated SQL:\n%s", result.get("sql"))
    logger.info("Raw Result:\n%s", result.get("data"))
    logger.info("=====================")

    return {
        "agent_output": result
    }


# =====================================================
# RAG Node
# =====================================================

def rag_node(state: AgentState):

    question = state["question"]

    print("\nExecuting RAG Agent...\n")

    result = rag_agent.answer(question)

    logger.info("===== RAG AGENT =====")
    logger.info("Question: %s", question)
    logger.info("Answer:\n%s", result.get("answer"))
    logger.info("Sources:\n%s", result.get("sources"))
    logger.info("=====================")

    return {
        "agent_output": result["answer"],
        "rag_documents": result["sources"]
    }

# =====================================================
# Response Node
# =====================================================

def response_node(state: AgentState):

    print("\nGenerating Final Response...\n")

    answer = response_agent.generate_response(
    question=state["question"],
    conversation_history=state["conversation_history"],
    planner=state["route"],
    agent_output=state["agent_output"],
    )

    logger.info("===== RESPONSE AGENT =====")
    logger.info("Planner: %s", planner)
    logger.info("Final Response:\n%s", answer)
    logger.info("==========================")

    return {
        "answer": answer
    }

# =====================================================
# Router Function
# =====================================================

def router(state: AgentState):

    return state["route"]


# =====================================================
# Build Workflow
# =====================================================

workflow = StateGraph(AgentState)


# Add Nodes

workflow.add_node(
    "planner",
    planner_node
)

workflow.add_node(
    "sql",
    sql_node
)

workflow.add_node(
    "rag",
    rag_node
)

workflow.add_node(
    "response",
    response_node
)

# Entry Point

workflow.set_entry_point("planner")


# Conditional Routing

workflow.add_conditional_edges(
    "planner",
    router,
    {
        "sql": "sql",
        "rag": "rag"
    }
)


# Finish Graph

workflow.add_edge(
    "sql",
    "response"
)

workflow.add_edge(
    "rag",
    "response"
)

workflow.add_edge(
    "response",
    END
)

# Compile Graph

graph = workflow.compile()