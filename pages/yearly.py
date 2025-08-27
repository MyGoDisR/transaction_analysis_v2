# Libraries
import streamlit as st
import pandas as pd
import altair as alt
import sys
import os
import utils.finance as finance
import utils.navigation as navigation
import requests
from forex_python.converter import CurrencyRates
from forex_python.bitcoin import BtcConverter
c = CurrencyRates()
#PLN_USD = c.get_rate('PLN', 'USD')
#PLN_EUR = c.get_rate('PLN', 'EUR')

# Security 
if "role_" not in st.session_state:
    st.switch_page("app.py")


if "lang" not in st.session_state:
    st.session_state.lang = 'ENG'
    lang_number = 0
if st.session_state.lang is None:
    lang_number = 0
elif st.session_state.lang == "ENG":
    lang_number = 0
elif st.session_state.lang == "PLN":
    lang_number = 1
navigation.menu()

translations = {
    "title": {"ENG": "Budget Overview", "POL": "Ogólny zarys budżetu"},
    "filtered_title": {"ENG": "Filter your transactions and view insights.", "POL": "Filtruj swoje transakcje and zobacz wnioski"},
    "sel_curr": {"ENG": "Currency", "POL": "Waluta"},
    "sel_year": {"ENG": "Choose Year:", "POL": "Wybierz rok:"},
    "expenses": {"ENG": "Overall Spending", "POL": "Ogólne wydatki"},
    "income": {"ENG": "Overall Inflows", "POL": "Ogólne wpłaty"},
    "food_e": {"ENG": "Food Expenses", "POL": "Wydatki - Żywność"},
    "house_e": {"ENG": "House Expenses", "POL": "Wydatki - Dom"},
    "beauty_e": {"ENG": "Beauty Expenses", "POL": "Wydatki - Kosmetyki"},
    "other_e": {"ENG": "Other Expenses", "POL": "Wydatki - Inne"},
    "sel_tags": {"ENG": "Select Tags", "POL": "Wybierz rodzaj"},
    "sel_date": {"ENG": "Select Date Range", "POL": "Wybierz zakres dat"},
    "sel_trans": {"ENG": "Filtered Transactions", "POL": "Wyfiltrowane transakcje"},
    "title_1": {"ENG": "Spending Over Time", "POL": "Wydatki z czasem"},
    "title_2": {"ENG": "Monthly Spending", "POL": "Wydatki miesięczne"}
}

######## Data #############################################################################

if len(os.listdir(f'Data/{st.session_state.role_}/Processed')) == 0:
    st.error('In order to see analysis please upload the data', width='stretch')
else:
    df = pd.read_csv(f'Data/{st.session_state.role_}/Processed/final_output.csv')

    df['Date'] = pd.to_datetime(df['Date'])
    df["Day"] = df["Date"].dt.day
    df['Month'] = df['Date'].dt.month
    df['Year'] = df['Date'].dt.year
    df['No. trans'] = df['Date'].count()
    df['Year-Month'] = (df['Year']).astype(str) + '-' +(df['Month']).astype(str)
 
    ########################################################################################## Title and Description
    st.title(translations["title"][st.session_state.lang])
    st.write(translations["filtered_title"][st.session_state.lang])

    curr = ["PLN", "EUR", "USD"]
    curr_selection = st.pills(translations["sel_curr"][st.session_state.lang], curr, selection_mode="single" )

    if curr_selection =="EUR":
        df['Amount'] = df['Amount'] * 0.23
        currency_icon = "€"
    elif curr_selection == "USD":
        df['Amount'] = df['Amount'] * 0.27
        currency_icon = "$"
    else:
        currency_icon = "zł"

    years = df.groupby('Year')
    selection = st.pills(translations["sel_year"][st.session_state.lang], years, selection_mode="single")

    # Filter the DataFrame
    if selection != None:  
        df = df[df['Year'] == selection].reset_index(drop=True)

    # KPI's
    KPI_list = [
        [translations["expenses"][st.session_state.lang], df[df['Tags'] != 'Inflows']['Amount'].sum()],
        [translations["income"][st.session_state.lang], df[df['Tags'] == 'Inflows']['Amount'].sum()],
        [translations["food_e"][st.session_state.lang], df[(df['Tags'] != 'Inflows') & (df['Tags'] == 'Food')]['Amount'].sum()],
        [translations["house_e"][st.session_state.lang], df[(df['Tags'] != 'Inflows') & (df['Tags'] == 'House appliencies')]['Amount'].sum()],
        [translations["beauty_e"][st.session_state.lang], df[(df['Tags'] != 'Inflows') & (df['Tags'] == 'Beauty')]['Amount'].sum()],
        [translations["other_e"][st.session_state.lang], df[(df['Tags'] != 'Inflows') & (df['Tags'] == 'Others')]['Amount'].sum()]
    ]
    # There will be a KPI's which gives the rough indicator
    row1 = st.columns(3)
    row2 = st.columns(3)

    for index, col in enumerate(row1 + row2):
        title = col.container(height=120)
        title.metric(KPI_list[index][0], str(round(KPI_list[index][1],2)) + " " + currency_icon)

    # Filters
    categories = st.multiselect(translations["sel_tags"][st.session_state.lang], options=df['Tags'].unique(), default=df['Tags'].unique())
    date_range = st.date_input(translations["sel_date"][st.session_state.lang], [df['Date'].min(), df['Date'].max()])
    start_date, end_date = date_range

    # Convert to datetime for comparison
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter the DataFrame
    df_ = df.iloc[:,:] # dismissing month and year
    dataframe_df = df_[(df_['Tags'].isin(categories)) & (df_['Date'] >= start_date) & (df_['Date'] <= end_date)]
    dataframe_df['Date'] = dataframe_df['Date'].dt.date

    # Display the filtered data
    st.write(f"### {translations["sel_trans"][st.session_state.lang]}")
    st.dataframe(dataframe_df[['Date','Desc','Tags','Amount']], use_container_width=True)

    # Line chart - Running balance
    st.write(f"### {translations["title_1"][st.session_state.lang]}")
    df['Week'] = df['Date'].dt.isocalendar().week
    chart_data = df[df['Tags'].isin(categories)].groupby('Week')['Amount'].sum().reset_index()

    area_chart = alt.Chart(chart_data).mark_area().encode(
        x="Week:T",
        y="Amount:Q",
        tooltip=['Week','Amount']
    )

    # Display the chart in Streamlit
    st.altair_chart(area_chart, use_container_width=True)

    # Bar chart 
    st.write(f'### {translations["title_2"][st.session_state.lang]}')
    df['Month'] = df['Date'].dt.month

    # Group by Month and Tags
    if selection != None: 
        grouped_data = df.groupby(['Month', 'Tags'], as_index=False)['Amount'].sum()
        # Create the bar chart using Altair
        chart = alt.Chart(grouped_data[grouped_data['Tags'].isin(categories)]).mark_bar().encode(
            x=alt.X('Month:O', title='Month'),
            y=alt.Y('Amount:Q', title = None),
            color=alt.Color('Tags:N', title='Tags'),  # Color based on Tags
            tooltip=['Month', 'Tags', 'Amount']  # Add tooltips for interactivity
        )
    else:
        grouped_data = df.groupby(['Year-Month', 'Tags'], as_index=False)['Amount'].sum()
        full_year_months = sorted(df['Year-Month'].unique())
        # Create the bar chart using Altair
        chart = alt.Chart(grouped_data[grouped_data['Tags'].isin(categories)]).mark_bar().encode(
            x=alt.X('Year-Month:O', title='Year-Month', sort=full_year_months),
            y=alt.Y('Amount:Q', title = None),
            color=alt.Color('Tags:N', title='Tags'),  # Color based on Tags
            tooltip=['Year-Month', 'Tags', 'Amount']  # Add tooltips for interactivity
        )

    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)