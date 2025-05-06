# Libraries
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import sys
import os
import algo
# FIXME: add year into selection or to inherit it from overview page

# Parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

######## Data #############################################################################
df = algo.fixing_type(algo.data_to_df('Data'))

df["Day"] = df["Date"].dt.day
df['Month'] = df['Date'].dt.month
df['Year'] = df['Date'].dt.year
df['No. trans'] = df['Date'].count()

########################################################################################## Title and Description
st.title("Budget Overview")
st.write("Filter your transactions and view insights.")

years = df.groupby('Year')
selection = st.pills("Choose Year: ", years, selection_mode="single")

# Filter the DataFrame
if selection != None:  
    df = df[df['Year'] == selection].reset_index(drop=True)

# KPI's
KPI_list = [
    ["Overall Spending", df[df['Type'] != 'Inflow']['Amount'].sum()],
    ["Overall Inflows", df[df['Type'] == 'Inflow']['Amount'].sum()],
    ["Food Expenses", df[(df['Type'] != 'Inflow') & (df['Type'] == 'Food')]['Amount'].sum()],
    ["House Expenses", df[(df['Type'] != 'Inflow') & (df['Type'] == 'House appliencies')]['Amount'].sum()],
    ["Beauty Expenses", df[(df['Type'] != 'Inflow') & (df['Type'] == 'Beauty')]['Amount'].sum()],
    ["Other Expenses", df[(df['Type'] != 'Inflow') & (df['Type'] == 'Others')]['Amount'].sum()]
]
# There will be a KPI's which gives the rough indicator
row1 = st.columns(3)
row2 = st.columns(3)

for index, col in enumerate(row1 + row2):
    title = col.container(height=120)
    title.metric(KPI_list[index][0], round(KPI_list[index][1],2))

# Filters
categories = st.multiselect("Select Type", options=df['Type'].unique(), default=df['Type'].unique())
date_range = st.date_input("Select Date Range", [df['Date'].min(), df['Date'].max()])
start_date, end_date = date_range
# Convert to datetime for comparison
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter the DataFrame
df = df.iloc[:,[0,2,3,4,5,6,7]] # dismissing month and year
dataframe_df = df[(df['Type'].isin(categories)) & (df['Date'] >= start_date) & (df['Date'] <= end_date)]
dataframe_df['Date'] = dataframe_df['Date'].dt.date

# Display the filtered data
st.write("### Filtered Transactions")
st.dataframe(dataframe_df, use_container_width=True)

# Line chart - Running balance
st.write("### Spending Over Time")
chart_data = df.groupby('Date')['Run_balance'].median().reset_index()
st.area_chart(chart_data.set_index('Date'), use_container_width=True)

# Bar chart 
st.write('### Monthly Spending')
if 'Inflow' in dataframe_df['Type']:
    bar_chart_df = df[dataframe_df['Type'] != 'Inflows']
else:
    bar_chart_df = df

# Add a Month column
bar_chart_df['Month'] = bar_chart_df['Date'].dt.month

# Group by Month and Type
grouped_data = bar_chart_df.groupby(['Month', 'Type'], as_index=False)['Amount'].sum()

# Create the bar chart using Altair
chart = alt.Chart(grouped_data).mark_bar().encode(
    x=alt.X('Month:O', title='Month'),
    y=alt.Y('Amount:Q', title = None),
    color=alt.Color('Type:N', title='Type'),  # Color based on Type
    tooltip=['Month', 'Type', 'Amount']  # Add tooltips for interactivity
)

# Display the chart in Streamlit
st.altair_chart(chart, use_container_width=True)