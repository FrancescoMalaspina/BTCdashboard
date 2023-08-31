import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Bitcoin Price Dashboard")

data = pd.read_csv("database/BTC-USD.csv")
dashboard_table = data.head(10)

st.plotly_chart(px.line(data, x='Date', y='Close', title='Bitcoin Price'))

st.write("Top 10 Rows of the Dataset:")
st.write(dashboard_table)