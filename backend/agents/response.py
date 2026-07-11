import pandas as pd

from langchain_core.prompts import ChatPromptTemplate

from backend.config.llm_factory import LLMFactory


PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are the final response formatter in a multi-agent medical AI system.

Your ONLY responsibility is to rewrite the output produced by another agent into a natural, professional, conversational response.

You are NOT an information retrieval agent.

Rules:

- Use the Agent Output as the ONLY source of factual information.
- Use the Conversation History ONLY to maintain conversational continuity (for example, understanding follow-up questions such as "What about him?" or "Can you explain that further?").
- Never use Conversation History to add new facts.
- Never invent, infer, or assume information.
- Never contradict the Agent Output.
- Never answer using your own knowledge.
- Never mention SQL, databases, tables, DataFrames, vector stores, documents, embeddings, planners, or internal agents.

If Planner = "sql":
- Explain the results naturally.
- Explain numbers in context.
- Summarize tables instead of reproducing them unless the table is very small.
- If no records are found, state that politely.
- If an error exists, explain it politely.

If Planner = "rag":
- Treat the Agent Output as the final answer.
- Improve only grammar, readability and flow.
- Preserve every fact.
- Do not remove or add information.

Return ONLY the final response.
"""
        ),
        (
            "human",
            """
Conversation History:
{conversation_history}

Current User Question:
{question}

Planner:
{planner}

Agent Output:
{agent_output}
"""
        ),
    ]
)


class ResponseAgent:

    def __init__(self):
        self.llm = LLMFactory.get_llm()
        self.chain = PROMPT | self.llm

    def _format_agent_output(self, agent_output):

        if isinstance(agent_output, pd.DataFrame):
            return agent_output.to_string(index=False)

        if isinstance(agent_output, dict):

            formatted = {}

            for key, value in agent_output.items():

                if isinstance(value, pd.DataFrame):
                    formatted[key] = value.to_string(index=False)
                else:
                    formatted[key] = value

            return formatted

        return agent_output

    def generate_response(
        self,
        question,
        conversation_history,
        planner,
        agent_output,
    ):

        formatted_output = self._format_agent_output(agent_output)

        response = self.chain.invoke(
            {
                "question": question,
                "conversation_history": conversation_history,
                "planner": planner,
                "agent_output": formatted_output,
            }
        )

        return response.content