

## app.py
```python
import streamlit as st
from chatbot import Chatbot

st.set_page_config(page_title="AI CSV Chatbot", layout="wide")
st.title("📊 AI CSV Chatbot")

# Sidebar - CSV upload
st.sidebar.header("Upload your CSV Data")
uploaded = st.sidebar.file_uploader("Select a CSV file", type="csv")

if uploaded:
    bot = Chatbot(uploaded)
    st.sidebar.success(f"Loaded: {bot.df.shape[0]} rows, {bot.df.shape[1]} cols")

    # Display the DataFrame
    st.subheader("Data Preview")
    st.dataframe(bot.df)

    if 'history' not in st.session_state:
        st.session_state.history = []

    user_input = st.text_input("You:", key="input")
    if user_input:
        with st.spinner():
            response, follow_ups = bot.ask(user_input)
        st.session_state.history.append(("user", user_input))
        st.session_state.history.append(("bot", response))

    for role, msg in st.session_state.history:
        if role == 'user':
            st.markdown(f"**You:** {msg}")
        else:
            st.markdown(f"**Bot:** {msg}")

    if st.session_state.history and st.session_state.history[-1][0]=='bot' and follow_ups:
        st.markdown("**Suggested follow-up questions:**")
        for q in follow_ups:
            st.write(f"- {q}")
else:
    st.info("Upload a CSV file to start chatting.")
