import streamlit as st

def render_sidebar():
    with st.sidebar:
        # 1. Logo at the top of the sidebar
        # You can use a local path "assets/logo.png" or a URL
        st.image(r"C:\Users\ranay\Desktop\life-sciences-ai-agent\frontend\components\logo.jpg")
        st.title("Medical AI Assistant")
        st.write("---")
        
        # 2. Chat History Section
        st.subheader("Chat History")
        
        # Mock history data (In production, pull this from a database or st.session_state)
        if "chat_history_list" not in st.session_state:
            st.session_state.chat_history_list = ["Symptoms Check - Jan 10", "Medication Query - Jan 09", "Diet Advice - Jan 05"]
        
        # Render history as clickable buttons
        for chat_title in st.session_state.chat_history_list:
            if st.button(chat_title, key=chat_title, use_container_width=True):
                st.info(f"Switching to: {chat_title}")
                # Here you would logic to load the specific chat into st.session_state.messages