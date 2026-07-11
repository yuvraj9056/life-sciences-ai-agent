import json
import os

from backend.graph.workflow import graph

MEMORY_FILE = "chat_memory.json"
MAX_HISTORY = 10


# ---------------- Memory ---------------- #

def load_memory():
    """Load all conversations from disk."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_memory(memory):
    """Persist conversations to disk."""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)


def add_message(memory, thread_id, role, content):
    """Add a message to a conversation."""
    if thread_id not in memory:
        memory[thread_id] = []

    memory[thread_id].append({
        "role": role,
        "content": content
    })


def build_prompt(memory, thread_id, question):
    """
    Build a prompt containing recent conversation history.
    """

    history = memory.get(thread_id, [])[-MAX_HISTORY:]

    conversation = []

    for msg in history:
        role = "User" if msg["role"] == "user" else "Assistant"
        conversation.append(f"{role}: {msg['content']}")

    history_text = "\n".join(conversation)

    return f"""You are continuing an ongoing conversation.

Conversation History:
{history_text}

Current User Question:
{question}
"""


# ---------------- CLI ---------------- #

def run_cli():

    memory = load_memory()

    print("\n===== LangGraph Chat =====")

    thread_id = input("Thread ID: ").strip()

    if not thread_id:
        thread_id = "default"

    print(f"Using thread: {thread_id}")
    print("Type 'clear' to erase this conversation.")
    print("Type 'exit' to quit.\n")

    while True:

        question = input("You: ").strip()

        if not question:
            continue

        if question.lower() == "exit":
            print("Goodbye!")
            break

        if question.lower() == "clear":
            memory[thread_id] = []
            save_memory(memory)
            print("Conversation cleared.\n")
            continue

        # Save user's message
        add_message(memory, thread_id, "user", question)

        # Build prompt with recent history
        prompt = build_prompt(memory, thread_id, question)

        # Invoke LangGraph
        result = graph.invoke({"question": question, 'conversation_history':prompt})

        answer = result.get("answer", result)

        print(f"\nAssistant:\n{answer}\n")

        # Save assistant response
        add_message(memory, thread_id, "assistant", answer)

        # Persist memory
        save_memory(memory)


if __name__ == "__main__":
    run_cli()