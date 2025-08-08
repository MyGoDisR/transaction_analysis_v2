# Libraries
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import sys
import os
import utils.finance as finance
from datetime import datetime
import matplotlib.pyplot as plt
import navigation

# Security 
if "role_" not in st.session_state:
    st.switch_page("app.py")

df = finance.fixing_type(finance.data_to_df_daniel('Data/Daniel'))

navigation.menu()

df["Day"] = df["Date"].dt.day
df['Month'] = df['Date'].dt.month
df['Year'] = df['Date'].dt.year
df['WeekNo'] = df['Date'].dt.isocalendar().week

st.title("Weekly overview")

months_names = ['January','February','March','April','May','June','July','August','September','October','November','December']
months = {'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,
          'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}
months2 = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',
           8:'August',9:'September',10:'October',11:'November',12:'December'}

list_ = [[],[],[]]

for ind,i in enumerate(df['Date'].dt.year.unique()):
  list_[0].append(f'{i}') # tab name, eq: "2021"
  list_[1].append(f'tab{ind}') # year number
  list_[2].append(df[df['Year'] == int(i)]) #specific dataframes Year

# Yearly Tabs
list_[1] = st.tabs(list_[0])

for year in range(0,len(list_[0])):
  with list_[1][year]:
    df_selected_year = list_[2][year]
    selection = st.pills("Choose Month: ", list(map(months2.get, df_selected_year['Month'].unique())), selection_mode="multi", key=f'month_pill_{list_[1][year]}')

    if selection:
      # Dataframe current selected month and year and specific filters
      df_curr_month = df_selected_year[df_selected_year['Month'].isin(map(months.get, selection))]
      
      # Filters based on Tags 
      categories = st.multiselect("Select Tags", options=df_curr_month['Tags'].unique(), default=df_curr_month['Tags'].unique(), key=f'type_filter_{list_[1][year]}')
      df_filtered = df_curr_month[df_curr_month['Tags'].isin(categories)]
      # Table Header
      st.write("Detailed table with transactions")

      ############## TABLE ##############################################################################################################################################
      st.dataframe(df_filtered.reset_index(drop=True).iloc[:,[0,7,5,3,-3]], use_container_width=True)

      ############## Bar Chart ##########################################################################################################################################
      st.write('### Weekly Spending')
      
      df_bar_chart = df_filtered.groupby(['WeekNo', 'Tags'], as_index=False)['Amount'].sum()
      
      chart = alt.Chart(df_bar_chart).mark_bar().encode(
        x=alt.X('WeekNo:O', title='Week'),
        y=alt.Y('Amount:Q', title = None),
        color=alt.Color('Tags:N', title='Tags'),  # Color based on Tags
        tooltip=['WeekNo', 'Tags', 'sum(Amount)'],  # Add tooltips for interactivity
        text=alt.Text('sum(Amount):Q', format='.0f')
      )
      # Display the chart in Streamlit
      st.altair_chart(chart, use_container_width=True)
    else:
      st.write('Please choose specific month')
    

    