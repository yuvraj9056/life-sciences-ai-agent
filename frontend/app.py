import streamlit as st
from components.sidebar import render_sidebar
from components.chat import render_chat_interface

# 1. Page Configuration (Must be the very first Streamlit command)
st.set_page_config(
    page_title="Medical AI Assistant",
    page_icon="⚕️",
    layout="wide"
)

# 2. Render Sidebar Component
render_sidebar()

# 3. Render Main Chat Component
render_chat_interface()