import streamlit as st

# Simulated graph.invoke() for illustration. 
# Replace this with your actual LangGraph / LangChain graph import.
def mock_graph_invoke(user_input):
    # your_graph.invoke({"messages": [("user", user_input)]})
    return f"This is a simulated Medical AI response to: '{user_input}'"

def render_chat_interface():
    st.subheader("Consultation Room")

    # Initialize session state for the current chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am your Medical AI Assistant. How can I help you today?"}
        ]

    # Display existing messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if user_input := st.chat_input("How can I help you Today ..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Generate AI response using your graph
        with st.chat_message("assistant"):
            with st.spinner("Analyzing data..."):
                # LINK YOUR GRAPH HERE:
                # response = graph.invoke({"messages": ...})
                ai_response = mock_graph_invoke(user_input) 
                st.markdown(ai_response)
                
        st.session_state.messages.append({"role": "assistant", "content": ai_response})