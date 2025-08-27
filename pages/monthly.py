# Libraries
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import utils.finance as finance
import utils.navigation as navigation
import os
import calendar
from datetime import date
from forex_python.converter import CurrencyRates
#c = CurrencyRates()
#PLN_USD = c.get_rate('PLN', 'USD')
#PLN_EUR = c.get_rate('PLN', 'EUR')

# Security 
if "role_" not in st.session_state:
  st.switch_page("app.py")

if st.session_state.lang is None:
    lang_number = 0
elif st.session_state.lang == "ENG":
    lang_number = 0
elif st.session_state.lang == "PLN":
    lang_number = 1
navigation.menu()

translations = {
    "title": {"ENG": "Monthly overview", "POL": "Analiza miesięczna"},
    "sel_curr": {"ENG": "Currency", "POL": "Waluta"},
    "sel_month": {"ENG": "Choose month:", "POL": "Wybierz miesiąc"},
    "expenses": {"ENG": "Overall Spending", "POL": "Ogólne wydatki"},
    "income": {"ENG": "Overall Inflows", "POL": "Ogólne wpłaty"},
    "food_e": {"ENG": "Food Expenses", "POL": "Wydatki - Żywność"},
    "house_e": {"ENG": "House Expenses", "POL": "Wydatki - Dom"},
    "beauty_e": {"ENG": "Beauty Expenses", "POL": "Wydatki - Kosmetyki"},
    "other_e": {"ENG": "Other Expenses", "POL": "Wydatki - Inne"},
    "sel_tags": {"ENG":"Select tags:", "POL":"Wybierz rodzaj:"},
    "title_1": {"ENG": "Detailed table with transactions", "POL": "Szczegółowa tablea z transakcjami"},
    "title_2": {"ENG": "'Weekly Spending", "POL": "Wydatki tygodniowe"},
    "title_3": {"ENG": "Spending during week", "POL": "Wydatki w ciągu tygodnia"},
    "title_4": {"ENG": "Spending over entire month of", "POL": "Wydatki w ciągu całego miesiąca ->"},
    "no_data_mes": {"ENG":"Please choose specific month", "POL":"Wybierz miesiąc aby zobaczyć analizę"}
}

if len(os.listdir(f'Data/{st.session_state.role_}/Processed')) == 0:
    st.error('In order to see analysis please upload the data', width='stretch')
else:
    df = pd.read_csv(f'Data/{st.session_state.role_}/Processed/final_output.csv')

    df['Date'] = pd.to_datetime(df['Date'])
    df["Day"] = df["Date"].dt.day
    df['Month'] = df['Date'].dt.month
    df['Year'] = df['Date'].dt.year
    df['WeekNo'] = df['Date'].dt.isocalendar().week


    st.title(translations["title"][st.session_state.lang])
    curr = ["PLN", "EUR", "USD"]
    curr_selection = st.pills(translations["sel_curr"][st.session_state.lang], curr, selection_mode="single", )
    if curr_selection =="EUR":
      df['Amount'] = round(df['Amount'] * 0.23,2)
      currency_icon = "€"
    elif curr_selection == "USD":
      df['Amount'] = round(df['Amount'] * 0.27,2)
      currency_icon = "$"
    else:
      currency_icon = "zł"

    months_names = {
      "jan":{"ENG":"January","POL":"Styczeń"},
      "feb":{"ENG":"February","POL":"Luty"},
      "mar":{"ENG":"March","POL":"Marzec"},
      "apr":{"ENG":"April","POL":"Kwiecień"},
      "may":{"ENG":"May","POL":"Maj"},
      "jun":{"ENG":"June","POL":"Czerwiec"},
      "jul":{"ENG":"July","POL":"Lipiec"},
      "aug":{"ENG":"August","POL":"Sierpień"},
      "sep":{"ENG":"September","POL":"Wrzesień"},
      "oct":{"ENG":"October","POL":"Pażdziernik"},
      "nov":{"ENG":"November","POL":"Listopad"},
      "dec":{"ENG":"December","POL":"Grudzień"},
    }
    months = {months_names["jan"][st.session_state.lang]:1,
              months_names["feb"][st.session_state.lang]:2,
              months_names["mar"][st.session_state.lang]:3,
              months_names["apr"][st.session_state.lang]:4,
              months_names["may"][st.session_state.lang]:5,
              months_names["jun"][st.session_state.lang]:6,
              months_names["jul"][st.session_state.lang]:7,
              months_names["aug"][st.session_state.lang]:8,
              months_names["sep"][st.session_state.lang]:9,
              months_names["oct"][st.session_state.lang]:10,
              months_names["nov"][st.session_state.lang]:11,
              months_names["dec"][st.session_state.lang]:12}
    
    months2 = {1:months_names["jan"][st.session_state.lang],
              2:months_names["feb"][st.session_state.lang],
              3:months_names["mar"][st.session_state.lang],
              4:months_names["apr"][st.session_state.lang],
              5:months_names["may"][st.session_state.lang],
              6:months_names["jun"][st.session_state.lang],
              7:months_names["jul"][st.session_state.lang],
              8:months_names["aug"][st.session_state.lang],
              9:months_names["sep"][st.session_state.lang],
              10:months_names["oct"][st.session_state.lang],
              11:months_names["nov"][st.session_state.lang],
              12:months_names["dec"][st.session_state.lang]}

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
        selection = st.pills(translations["sel_month"][st.session_state.lang], list(map(months2.get, df_selected_year['Month'].unique())), selection_mode="multi", key=f'month_pill_{list_[1][year]}')
        if selection:
          # Dataframe current selected month and year and specific filters
          df_curr_month = df_selected_year[df_selected_year['Month'].isin(map(months.get, selection))]

          # KPI's
          KPI_list = [
              [translations["expenses"][st.session_state.lang], df_curr_month[df_curr_month['Tags'] != 'Inflows']['Amount'].sum()],
              [translations["income"][st.session_state.lang], df_curr_month[df_curr_month['Tags'] == 'Inflows']['Amount'].sum()],
              [translations["food_e"][st.session_state.lang], df_curr_month[(df_curr_month['Tags'] != 'Inflows') & (df_curr_month['Tags'] == 'Food')]['Amount'].sum()],
              [translations["house_e"][st.session_state.lang], df_curr_month[(df_curr_month['Tags'] != 'Inflows') & (df_curr_month['Tags'] == 'House appliencies')]['Amount'].sum()],
              [translations["beauty_e"][st.session_state.lang], df_curr_month[(df_curr_month['Tags'] != 'Inflows') & (df_curr_month['Tags'] == 'Beauty')]['Amount'].sum()],
              [translations["other_e"][st.session_state.lang], df_curr_month[(df_curr_month['Tags'] != 'Inflows') & (df_curr_month['Tags'] == 'Others')]['Amount'].sum()]
          ]
          # There will be a KPI's which gives the rough indicator
          row1 = st.columns(3)
          row2 = st.columns(3)

          for index, col in enumerate(row1 + row2):
              title = col.container(height=120)
              title.metric(KPI_list[index][0], str(round(KPI_list[index][1],2)) + " " + currency_icon)
          # Filters based on Tags 
          categories = st.multiselect(translations["sel_tags"][st.session_state.lang], options=df_curr_month['Tags'].unique(), default=df_curr_month['Tags'].unique(), key=f'type_filter_{list_[1][year]}')
          df_filtered = df_curr_month[df_curr_month['Tags'].isin(categories)]
          # Table Header
          st.write(translations["title_1"][st.session_state.lang])
          ############## TABLE ##############################################################################################################################################
          st.dataframe(df_filtered.reset_index(drop=True).iloc[:,[0,1,4,3]], use_container_width=True) 

          ############## Bar Chart ##########################################################################################################################################
          st.write(f'### {translations["title_2"][st.session_state.lang]}')
          df_bar_chart = df_filtered.groupby(['WeekNo', 'Tags'], as_index=False)['Amount'].sum()
          df_bar_chart['% of all'] = round(df_bar_chart['Amount'] / df_bar_chart.groupby('WeekNo')['Amount'].transform(func=sum) * 100,2)
          chart = alt.Chart(df_bar_chart).mark_bar().encode(
            x=alt.X('WeekNo:O', title='Week'),
            y=alt.Y('Amount:Q', title = None),
            color=alt.Color('Tags:N', title='Tags'),  # Color
            tooltip=['WeekNo', 'Tags', 'sum(Amount)', '% of all'],  # Tooltip
            text=alt.Text('sum(Amount):Q', format='.0f')
          )
          st.altair_chart(chart, use_container_width=True)

          st.write(f'### {translations["title_3"][st.session_state.lang]}')
          df_filtered['Day_name'] = df_filtered['Date'].dt.day_name()
          df_table = df_filtered[df_filtered['Tags'] != "Inflows"]
          df_table['Date'] = pd.to_datetime(df_table['Date']).dt.date
          spend_map = df_table.groupby('Date')['Amount'].sum().to_dict()

          df_week = df_filtered.groupby(['Day_name','Tags'], as_index=False)['Amount'].sum()
          weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

          chart = alt.Chart(df_week[df_week['Tags'].isin(categories)]).mark_bar().encode(
                  x=alt.X('Day_name:O', title='Days', sort=weekday_order),
                  y=alt.Y('Amount:Q', title = None),
                  color=alt.Color('Tags:N', title='Tags'),  # Color
                  tooltip=['Day_name', 'Tags', 'Amount']  # Tooltip
              )

          # Display the chart in Streamlit
          st.altair_chart(chart, use_container_width=True)
          latest_month = (df_filtered['Month'].unique()[-1])
          selection_ = st.pills(translations["sel_month"][st.session_state.lang], list(map(months2.get, df_filtered['Month'].unique())), selection_mode="single", key=f'month_pills_{list_[1][year]}_')
          if selection_:
            df_cal_month = df_filtered[df_filtered['Month'] == months[selection_]]
          else:
            df_cal_month = df_filtered[df_filtered['Month'] == latest_month]
          df_cal_month.reset_index(drop=True, inplace=True)
          year = df_cal_month['Year'][0]
          month = df_cal_month['Month'][0]
          days_in_month = calendar.monthrange(year, month)[1]
          dates = [date(year, month, day) for day in range(1, days_in_month + 1)]

          calendar_rows = []
          week = [''] * 7 
          for dt in dates:
              dow = dt.weekday() 
              content = f"[{dt.day}]\n${spend_map.get(dt, 0):.2f}"
              week[dow] = content

              if dow == 6 or dt.day == days_in_month:
                  calendar_rows.append(week)
                  week = [''] * 7 

          calendar_df = pd.DataFrame(calendar_rows, columns=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])

          def extract_amount(cell):
            try:
                return round(float(cell.split('$')[1]),2)
            except:
                return None
          st.write(f'### {translations["title_4"][st.session_state.lang]} {year}-{months2[latest_month] if selection_ is None else selection_}')
          if curr_selection =="EUR":
            heatmap_df = calendar_df.applymap(extract_amount)
            st.table(heatmap_df.style
                    .format('{:,.2f} €')
                    .background_gradient(cmap='YlOrRd', axis=None))
          elif curr_selection =="USD":
            heatmap_df = calendar_df.applymap(extract_amount)
            st.table(heatmap_df.style
                    .format('{:,.2f} $')
                    .background_gradient(cmap='YlOrRd', axis=None))
          elif curr_selection == "PLN" or curr_selection==None:
            heatmap_df = calendar_df.applymap(extract_amount)
            st.table(heatmap_df.style
                    .format('{:,.2f} zł')
                    .background_gradient(cmap='YlOrRd', axis=None))
        else:
          st.write(translations["no_data_mes"][st.session_state.lang])