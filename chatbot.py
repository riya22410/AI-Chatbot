import os
import pandas as pd
import openai
import streamlit as st
from dotenv import load_dotenv
from utils import plot_df, forecast_series

class Chatbot:
    def __init__(self, csv_file):
        load_dotenv()
        self.df = pd.read_csv(csv_file)
        self.messages = []
        # OpenAI & Azure config
        openai.api_type = "azure"
        openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
        openai.api_version = "2023-05-15"
        openai.api_key = os.getenv("AZURE_OPENAI_KEY")
        self.azure_deployment = os.getenv("AZURE_DEPLOYMENT_NAME")

    def ask(self, user_prompt: str):
        # Append user
        self.messages.append({"role":"user","content":user_prompt})
        # Initial system
        if len(self.messages)==1:
            cols = ", ".join(self.df.columns)
            sys_msg = (
                f"You are a data assistant. The user has uploaded a CSV with columns: {cols}. "
                "Answer precisely and when they request visuals or forecasts, generate code accordingly."
            )
            self.messages.insert(0, {"role":"system","content":sys_msg})
        # Main completion
        resp = openai.ChatCompletion.create(
            engine=self.azure_deployment,
            messages=self.messages,
            temperature=0.2,
        )
        answer = resp.choices[0].message.content.strip()
        self.messages.append({"role":"assistant","content":answer})

        # Execute dynamic plot or forecast
        if "plot" in user_prompt.lower():
            plot_df(self.df, user_prompt)
        if "forecast" in user_prompt.lower():
            forecast_series(self.df, user_prompt)

        # Get dynamic follow-ups
        follow_ups = self._generate_followups()
        return answer, follow_ups

    def _generate_followups(self):
        prompt = (
            "Based on the conversation and data context, suggest 3 concise follow-up questions "
            "the user might ask next. List them as bullet points without numbering."
        )
        messages = [
            {"role":"system","content":"You are an expert in user engagement."},
            *self.messages,
            {"role":"user","content":prompt}
        ]
        resp = openai.ChatCompletion.create(
            engine=self.azure_deployment,
            messages=messages,
            temperature=0.7,
        )
        # parse bullets
        text = resp.choices[0].message.content.strip()
        return [line.strip('- ').strip() for line in text.splitlines() if line.strip()]
