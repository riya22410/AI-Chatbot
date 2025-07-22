
---

## app.py
```python
import streamlit as st
from chatbot import Chatbot

st.set_page_config(page_title="AI CSV Chatbot", layout="wide")
st.title("📊 AI Chatbot with CSV Input and Visualization")

# Sidebar: CSV upload
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    # Initialize chatbot with DataFrame
    bot = Chatbot(uploaded_file)
    st.sidebar.success("CSV loaded: {} rows x {} columns".format(bot.df.shape[0], bot.df.shape[1]))

    # Chat interface
    st.header("Chat")
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("You:")
    if user_input:
        with st.spinner("Thinking..."):
            response, follow_ups = bot.ask(user_input)
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Bot", response))
        # Display chat
        for speaker, text in st.session_state.chat_history:
            if speaker == "You":
                st.markdown(f"**You:** {text}")
            else:
                st.markdown(f"**Bot:** {text}")
        # Show follow-ups
        if follow_ups:
            st.markdown("**Possible follow-up questions:**")
            for q in follow_ups:
                st.markdown(f"- {q}")
else:
    st.info("Upload a CSV file to get started.")
