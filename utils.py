import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from statsmodels.tsa.arima.model import ARIMA


def plot_df(df: pd.DataFrame, prompt: str):
    '''Simple parser: expects 'plot {column} over {x_col}' or similar.'''
    # For demonstration: plot first two numeric columns
    numeric = df.select_dtypes('number').columns
    if len(numeric) >= 2:
        x, y = numeric[0], numeric[1]
        fig, ax = plt.subplots()
        ax.plot(df[x], df[y])
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.set_title(f"{y} vs {x}")
        st.pyplot(fig)


def forecast_series(df: pd.DataFrame, prompt: str):
    '''Select first date-like index and numeric series to forecast.'''
    # very basic: assume first column is date, second is value
    df2 = df.copy()
    df2.iloc[:,0] = pd.to_datetime(df2.iloc[:,0])
    df2.set_index(df2.columns[0], inplace=True)
    ts = df2.iloc[:,0]
    # fit ARIMA
    model = ARIMA(ts, order=(1,1,1)).fit()
    n = 6  # default periods ahead
    fc = model.forecast(steps=n)
    fig, ax = plt.subplots()
    ts.plot(ax=ax)
    fc.plot(ax=ax)
    ax.set_title("Forecast")
    st.pyplot(fig)
    return df2.columns[0]
