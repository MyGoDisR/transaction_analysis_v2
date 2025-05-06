# Libraries
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import sys
import os
import algo
from datetime import datetime
import matplotlib.pyplot as plt

df = algo.fixing_type(algo.data_to_df('Data'))

df["Day"] = df["Date"].dt.day
df['Month'] = df['Date'].dt.month
df['Year'] = df['Date'].dt.year

st.title("Yearly overview")

list_ = [[],[],[]]

for ind,i in enumerate(df['Date'].dt.year.unique()):
  list_[0].append(f'{i}')
  list_[1].append(f'tab{ind}')
  list_[2].append(df[df['Year'] == int(i)])
# Yearly Tabs
list_[1] = st.tabs(list_[0])

for year in range(0,len(list_[0])):

    with list_[1][year]:
    # KPI's
        KPI_list = [
            ["Total Spending", list_[2][year][list_[2][year]['C/D'] == "C"]['Amount'].sum()],
            ["Total Income", list_[2][year][list_[2][year]['C/D'] == "D"]['Amount'].sum()],
            ["Savings", list_[2][year][list_[2][year]['Type'] == 'Savings']['Amount'].sum()],#list_[2][year][list_[2][year]['Desc'].str.contains('SAVINGS', case=False, na=False)]['Amount'].sum()],
            ["Expenses - Rent", list_[2][year][list_[2][year]['Type'] == 'Rent']['Amount'].sum()],
            ["Expenses - Groceries", list_[2][year][list_[2][year]['Type'] == 'Food']['Amount'].sum()],
            ["Expenses - Other", list_[2][year][list_[2][year]['Type'].isin(['Other','Beauty','Commute','Clothing','Outting','Necessities','Hobby','House appliencies'])]['Amount'].sum()]
        ]
        if year-1 >= 0:
            df_CY = list_[2][year]
            df_PY = list_[2][year-1] 
            df_PY_notfull = 'To be done'
            YoY_list = [
                round((df_CY[df_CY['C/D'] == "C"]['Amount'].sum() - df_PY[df_PY['C/D'] == "C"]['Amount'].sum()) / (df_PY[df_PY['C/D'] == "C"]['Amount'].sum()) * 100,2),
                round((df_CY[df_CY['C/D'] == "D"]['Amount'].sum() - df_PY[df_PY['C/D'] == "D"]['Amount'].sum()) / (df_PY[df_PY['C/D'] == "D"]['Amount'].sum()) * 100,2),
                round((df_CY[df_CY['Type'] == 'Savings']['Amount'].sum() - df_PY[df_PY['Type'] == 'Savings']['Amount'].sum()) / (df_PY[df_PY['Type'] == 'Savings']['Amount'].sum()) * 100,2),
                round((df_CY[df_CY['Type'] == 'Rent']['Amount'].sum() - df_PY[df_PY['Type'] == 'Rent']['Amount'].sum()) / (df_PY[df_PY['Type'] == 'Rent']['Amount'].sum()) * 100,2),
                round((df_CY[df_CY['Type'] == 'Food']['Amount'].sum() - df_PY[df_PY['Type'] == 'Food']['Amount'].sum()) / (df_PY[df_PY['Type'] == 'Food']['Amount'].sum()) * 100,2),
                round((df_CY[df_CY['Type'].isin(['Other','Beauty','Commute','Clothing','Outting','Necessities','Hobby','House appliencies'])]['Amount'].sum() - df_PY[df_PY['Type'].isin(['Other','Beauty','Commute','Clothing','Outting','Necessities','Hobby','House appliencies'])]['Amount'].sum()) / (df_PY[df_PY['Type'].isin(['Other','Beauty','Commute','Clothing','Outting','Necessities','Hobby','House appliencies'])]['Amount'].sum()) * 100,2)
            ]
        else:
             YoY_list = ["","","","","",""]

        # KPI's
        row1 = st.columns(3)
        row2 = st.columns(3)


        for index, col in enumerate(row1 + row2):
            if year-1 >= 0:
                title = col.container(height=125)
                title.metric(KPI_list[index][0], round(KPI_list[index][1],2),f'{YoY_list[index]} %')
            elif year == len(list_[0]):
                title = col.container(height=125)
                title.metric(KPI_list[index][0], round(KPI_list[index][1],2),f'{YoY_list[index]} %')
                st.write('YoY wrong')
            else:
                title = col.container(height=125)
                title.metric(KPI_list[index][0], round(KPI_list[index][1],2))
        
        # Line Chart
        # Group by Month and Type
        df_chart = list_[2][year][list_[2][year]['Type'].isin(['Other','Beauty','Commute','Clothing','Outting','Necessities','Hobby','House appliencies','Food', 'Outflow'])].groupby(['Month','Type'], as_index=False)['Amount'].sum()

        # Create the bar chart using Altair
        chart = alt.Chart(df_chart).mark_bar().encode(
            x=alt.X('Month:O', title='Month'),
            y=alt.Y('Amount:Q', title = None),
            color=alt.Color('Type:N', title='Type'),  # Color based on Type
            tooltip=['Month', 'Type', 'Amount']  # Add tooltips for interactivity
        )

        # Display the chart in Streamlit
        st.write('Transactions type bu Month')
        st.altair_chart(chart, use_container_width=True)

        # Pie Chart & Bar Chart 
        col1, col2 = st.columns(2)

        with col1:
            st.write('Spending categories distribution')
            st.bar_chart(list_[2][year][(list_[2][year]['Type'] != "Inflow") & (list_[2][year]['Type'] != "Outflow") & (list_[2][year]['Type'] != "Salary") & (list_[2][year]['Type'] != "FX_exchange") & (list_[2][year]['Type'] != "Savings")].groupby('Type')['Amount'].sum().sort_values(ascending=True), horizontal=True, height=250, use_container_width=True)        
    
        with col2:
            st.write('Spending categories distribution')

            df_piechart = list_[2][year][(list_[2][year]['Type'] != 'Salary') & (list_[2][year]['Type'] != 'Inflow')]
            df_piechart['Category'] = 'Others'

            df_piechart.loc[df_piechart['Type'].isin(['Other','Beauty','Commute','Clothing','Outting','Necessities','Hobby','House appliencies','Food', 'Outflow','Rent','Food']), 'Category'] = 'Live'
            df_piechart.loc[df_piechart['Type'].str.contains("Savings", case=False, na=False), 'Category'] = "Savings"
    
            fig1, ax1 = plt.subplots(facecolor='#0E1117')
            patches, texts, pcts = ax1.pie(df_piechart.groupby('Category')['Amount'].sum(), autopct='%1.1f%%',
                    shadow=True, startangle=90, textprops={'size': 'x-large'})#dict(color="w"))
            ax1.set_facecolor("#0E1117")
            #ax1.set(pcts, color='white', fontweight='bold')
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            fig1.legend()
            st.pyplot(fig1, use_container_width=True)
                
        # Table with transactions
        st.write("Detailed table with transactions")
        df_df = list_[2][year].iloc[:,[0,3,7,5]].set_index('Date')
        #df_df['Desc'].strip('48794959772')
        st.dataframe(df_df, use_container_width=True)
                