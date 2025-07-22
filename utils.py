import json
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import openai
from statsmodels.tsa.arima.model import ARIMA

azure_conf = st.secrets["azure_openai"]
openai.api_type = azure_conf["API_TYPE"]
openai.api_base = azure_conf["API_BASE"]
openai.api_version = azure_conf["API_VERSION"]
openai.api_key = azure_conf["API_KEY"]
azure_deployment = azure_conf["DEPLOYMENT_NAME"]

def plot_df(df: pd.DataFrame, prompt: str):
    cols = df.columns.tolist()
    schema_prompt = (
        f"Given dataframe columns: {cols}, parse this instruction: '{prompt}'. "
        "Respond only in JSON with keys: plot_type (e.g. line,histogram,bar), x (column or null), y (column or null), group (column or null)."
    )
    resp = openai.ChatCompletion.create(
        deployment_id=self.azure_deployment
        messages=[{"role":"user","content":schema_prompt}],
        temperature=0,
    )
    spec = json.loads(resp.choices[0].message.content)
    fig, ax = plt.subplots()
    if spec['plot_type'] == 'histogram':
        df[spec['x']].hist(ax=ax)
    elif spec['plot_type'] == 'bar':
        df.groupby(spec['x'])[spec['y']].mean().plot.bar(ax=ax)
    else:
        x = spec.get('x') or df.index
        y = spec.get('y')
        df.plot(x=x, y=y, ax=ax)
    ax.set_title(prompt)
    st.pyplot(fig)

def forecast_series(df: pd.DataFrame, prompt: str):
    cols = df.columns.tolist()
    schema_prompt = (
        f"Given dataframe columns: {cols}, parse this forecast request: '{prompt}'. "
        "Respond only in JSON with keys: date_col, value_col, periods (integer)."
    )
    resp = openai.ChatCompletion.create(
        engine=azure_deployment,
        messages=[{"role":"user","content":schema_prompt}],
        temperature=0,
    )
    spec = json.loads(resp.choices[0].message.content)
    df2 = df.copy()
    df2[spec['date_col']] = pd.to_datetime(df2[spec['date_col']])
    df2.set_index(spec['date_col'], inplace=True)
    ts = df2[spec['value_col']]
    model = ARIMA(ts, order=(1,1,1)).fit()
    fc = model.forecast(steps=spec['periods'])
    fig, ax = plt.subplots()
    ts.plot(ax=ax)
    fc.plot(ax=ax)
    ax.set_title(prompt)
    st.pyplot(fig)
