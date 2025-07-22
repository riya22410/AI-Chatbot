import pandas as pd
import openai
import streamlit as st
from utils import plot_df, forecast_series

class Chatbot:
    def __init__(self, csv_file):
        self.df = pd.read_csv(csv_file)
        self.messages = []
        # Azure OpenAI config from Streamlit secrets
        azure_conf = st.secrets["azure_openai"]
        openai.api_type = azure_conf["API_TYPE"]
        openai.api_base = azure_conf["API_BASE"]
        openai.api_version = azure_conf["API_VERSION"]
        openai.api_key = azure_conf["API_KEY"]
        self.azure_deployment = azure_conf["DEPLOYMENT_NAME"]

    def ask(self, user_prompt: str):
        self.messages.append({"role": "user", "content": user_prompt})
        if len(self.messages) == 1:
            cols = ", ".join(self.df.columns)
            sys_msg = (
                f"You are a data assistant. The user has uploaded a CSV with columns: {cols}. "
                "Answer precisely and when they request visuals or forecasts, generate code accordingly."
            )
            self.messages.insert(0, {"role": "system", "content": sys_msg})
        resp = openai.ChatCompletion.create(
            deployment_id=self.azure_deployment,  # ✅ Azure-specific parameter
            messages=self.messages,
            temperature=0.2,
        )
        answer = resp.choices[0].message.content.strip()
        self.messages.append({"role": "assistant", "content": answer})
        if "plot" in user_prompt.lower():
            plot_df(self.df, user_prompt)
        if "forecast" in user_prompt.lower():
            forecast_series(self.df, user_prompt)
        follow_ups = self._generate_followups()
        return answer, follow_ups

    def _generate_followups(self):
        prompt = (
            "Based on the conversation and data context, suggest 3 concise follow-up questions "
            "the user might ask next. List them as bullet points without numbering."
        )
        messages = [
            {"role": "system", "content": "You are an expert in user engagement."},
            *self.messages,
            {"role": "user", "content": prompt}
        ]
        resp = openai.ChatCompletion.create(
            deployment_id=self.azure_deployment,  # ✅ Fix here too
            messages=messages,
            temperature=0.7,
        )
        text = resp.choices[0].message.content.strip()
        return [line.strip('- ').strip() for line in text.splitlines() if line.strip()]
