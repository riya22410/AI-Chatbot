import os
import pandas as pd
import openai
from utils import plot_df, forecast_series

class Chatbot:
    def __init__(self, csv_file):
        # load DataFrame
        self.df = pd.read_csv(csv_file)
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def ask(self, user_prompt: str):
        # build system/context prompt
        context = (
            f"You are a data assistant. The user has uploaded a CSV with columns: {', '.join(self.df.columns)}. "
            f"Provide concise answers based on this data."
        )
        messages = [
            {"role": "system", "content": context},
            {"role": "user", "content": user_prompt}
        ]
        # call OpenAI
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.2,
        )
        answer = resp.choices[0].message.content.strip()

        # detection: plot
        if "plot" in user_prompt.lower():
            plot_df(self.df, user_prompt)
        # detection: forecast
        follow = []
        if "forecast" in user_prompt.lower():
            col = forecast_series(self.df, user_prompt)
            follow.append(f"Would you like a forecast plot for {col}?" )

        # generate follow-up suggestions
        follow.extend(self._gen_followups())
        return answer, follow

    def _gen_followups(self):
        # simple static ideas
        return [
            "Can you drill down by specific category?",
            "Do you want summary statistics for the dataset?",
            "Would you like to see missing-value analysis?"
        ]
