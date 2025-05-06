# Libraries
import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
import algo
import altair as alt
import app

# Parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

df = algo.fixing_type(algo.data_to_df('Data')).iloc[:,:]

df['Month'] = df['Date'].dt.month
df['Year'] = df['Date'].dt.year
df['Year-Month'] = df['Date'].dt.strftime("%Y-%m")

# st.bar_chart(df[df['Type'] == 'Salary'].groupby(['Year-Month']).agg(total_savings=('Amount', 'sum')))

# st.dataframe(df.loc[df['Desc'].str.contains('SAVINGS', case=False, na=False)].groupby(['Year','Month']).agg(total_savings=('Amount', 'sum')))

# st.bar_chart(df.loc[df['Desc'].str.contains('SAVINGS', case=False, na=False)].groupby(['Year-Month']).agg(total_savings=('Amount', 'sum')))

#st.bar_chart(df.loc[df['Desc'].str.contains('SAVINGS', case=False, na=False)].groupby(['Year','Month'], as_index=False), x='Date',y='Amount')

st.write()

st.dataframe(df[(df['Type'] != 'Salary') & (df["Type"] != "Savings")])

st.dataframe(df.loc[df['Type']=='Inflow'])

#st.dataframe(df.loc[df['Desc'].str.contains('Daniel BNP', case=False, na=False)])