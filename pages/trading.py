import streamlit as st
import utils.trading as trading
import utils.navigation as navigation
import pandas as pd
import numpy as np
from time import sleep
import sqlite3
from  utils import queries as qs
from datetime import datetime as dt

from forex_python.bitcoin import BtcConverter

import yfinance as yf

import os
import requests

# Security 
if "role_" not in st.session_state:
    st.switch_page("app.py")

if 'data' not in st.session_state:
    data = pd.DataFrame({'Ticker':[],'Purchase Date':[],'Quantity':[],'Purchase Price':[]})
    st.session_state.data = data

if "radio_sel" not in st.session_state:
    st.session_state.radio_sel = "Portfolio"

navigation.menu()

def callback():
    edited_rows = st.session_state["data_editor"]["edited_rows"]
    rows_to_delete = []

    for idx, value in edited_rows.items():
        if value["X"] is True:
            rows_to_delete.append(idx)

        st.session_state.data = (
            st.session_state.data.drop(rows_to_delete, axis=0).reset_index(drop=True)
            )

columns = st.session_state.data.columns
column_config = {column: st.column_config.Column(disabled=True) for column in columns}

modified_df = st.session_state.data.copy()
modified_df["X"] = False
# Make Delete be the first column
modified_df = modified_df[["X"] + modified_df.columns[:-1].tolist()]

translations = {
    "title": {"ENG": "Finance Data", "POL": "Dane Finansowe"},
    "info_mess1": {"ENG": "You do not input any trading data yet", "POL": "Nie masz jeszcze zadnych danych finanowych"},
    "info_mess2": {"ENG": "In order to change that please provide:", "POL": "Jezeli chcesz to zmienic prosze dodaj:"},
    "choose_file_": {"ENG": "Choose a CSV file", "POL": "Wybierz pliki CSV"},
    "type_mess": {"ENG": "we do not support other file types then csv", "POL": "Aplikacja nie wspiera pliki innego typu niż csv"},
    "error_mess1":{'ENG':'Please provide correct Ticker', "POL":"Podaj poprawny Ticker"},
    "error_mess2":{'ENG':'Please provide correct date format dd/mm/yyyy', "POL":"Podaj poprawny format daty dd/mm/yyyy"},
    "error_mess3":{'ENG':'Please provide volume', "POL":"Podaj ilość"},
    "error_mess4":{'ENG':'Please provide purchase price. If you do not know the price please leave it blank', "POL":"Podaj wartość zakupu. Jak nie znasz zostaw puste"},
    "data_":{'ENG':'Purch. Date (Y-m-d)', "POL":'Data Zakupu (Y-m-d)'},
    "volume_":{'ENG':'Volume', "POL":"Ilość"},
    "purchase_price":{'ENG':'Purchase price', "POL":"Cena zakupu"},
    "button_1":{'ENG':'Submit', "POL":"Zatwierdź"},
    "button_2":{'ENG':'Show analysis', "POL":"Pokaz analizę"},
    "conn_error":{'ENG':'Check your connection', "POL":"Sprawdź swoje połączenie"},
    "kpi_1":{'ENG':'Total Portoflio Value', "POL":"Wartość całego portfolio"},
    "kpi_2":{'ENG':'ATH (last 30 days)', "POL":"ATH (ostatnie 30 dni)"},
    "kpi_3":{'ENG':'ATL (last 30 days)', "POL":"ATL (ostatnie 30 dni)"},
    "kpi_4":{'ENG':'Profit/Loss', "POL":"Zysk/Strata"},
    "":{'ENG':['Portoflio','Single Transactions'], "POL":['Portoflio','Pojedyncze Transakcje']}
}

st.title(translations["title"][st.session_state.lang])

# Creating conection to db
con = qs.get_connection('db/users_.db')
cursor = con.cursor()

df_portfolio = pd.read_sql_query(f"SELECT * FROM user_portfolio WHERE login = ?;", con, params=(st.session_state.role_,))

if df_portfolio.empty:
    st.write(translations["info_mess1"][st.session_state.lang])
    st.write(translations["info_mess2"][st.session_state.lang])
    uploaded_files = st.file_uploader(translations["choose_file_"][st.session_state.lang], accept_multiple_files=True)
    for uploaded_file in uploaded_files:
        suffix = uploaded_file.name.split('.')[-1]
        if suffix == 'csv':
            df = pd.read_csv(uploaded_file, delimiter=';')
        else:
            st.write(translations["type_mess"][st.session_state.lang])

    def add_dfForm():
        row = pd.DataFrame({'Ticker':[str.upper(st.session_state.ticker)],
                'Purchase Date':[st.session_state.p_date],
                'Quantity':[st.session_state.quant],
                "Purchase Price":[st.session_state.p_price]})
        
        st.session_state.data = pd.concat([st.session_state.data, row])
    
    def error_message():
        if sum(i) + 1 == 10:
            st.error(translations["error_mess1"][st.session_state.lang])
        elif sum(i) + 2 == 10:
            st.error(translations["error_mess2"][st.session_state.lang])
        elif sum(i) + 3 == 10:
            st.error(translations["error_mess3"][st.session_state.lang])
        else:
            st.error(translations["error_mess4"][st.session_state.lang])
        return None

    dfForm = st.form(key='dfForm', width='content')
    with dfForm:
        trade = []
        dfColumns = st.columns(4)
        with dfColumns[0]:
            st.text_input('Ticker', key='ticker')
        with dfColumns[1]:
            st.text_input(translations["data_"][st.session_state.lang], key='p_date')
        with dfColumns[2]:
            st.text_input(translations["volume_"][st.session_state.lang], key='quant')
        with dfColumns[3]:
            st.text_input(translations["purchase_price"][st.session_state.lang], key='p_price')
        
        i = []      
        if len(st.session_state.ticker) != 0 and len(st.session_state.ticker) < 10:
            i.append(1)
            trade.append(st.session_state.ticker)
            
        if len(st.session_state.p_date) == 10:
            i.append(2)
            trade.append(st.session_state.p_date)

        if len(st.session_state.quant) > 0:
            i.append(3)
            trade.append(st.session_state.quant)

        if len(st.session_state.p_price) >= 0:
            i.append(4)
            trade.append(st.session_state.p_price)
        
        st.form_submit_button(translations["button_1"][st.session_state.lang], on_click=add_dfForm if sum(i) == 10 else error_message)

    data = st.session_state.data
    # Change the button to past data to db and the analysis will be shown
    # After pressing the filled form should disappear
    # Show dataframe with just added tickers
    if len(st.session_state.data)>0:
        if st.button(translations["button_2"][st.session_state.lang]):

            df_all_trades = pd.DataFrame()
            df_pl = pd.DataFrame()
            df_trades_all = []
            last_table = st.session_state.data.copy()
            # Purchase Price | Latest available Price | P/L | Value_gain
            last_table['Purchase Price'] = 0
            last_table['Latest Available Price'] = 0
            last_table['P/L'] = 0
            last_table['Value Gain'] = 0
            
            for _trade in range(0,len(data)):
                df_trade = yf.download(data.iloc[_trade,0],data.iloc[_trade,1],dt.today().strftime('%Y-%m-%d'))
                df_trade.columns = ['{}-{}'.format(*col) for col in df_trade.columns]
                if len(df_trade) < 2:
                    st.write(translations["conn_error"][st.session_state.lang])
                    sleep(1)
                    st.switch_page('pages/trading.py')
                if float(data.iloc[_trade,-1]) >= df_trade.iloc[0,2] and float(data.iloc[_trade,-1]) <= df_trade.iloc[0,1].astype(float):
                    df_trade.iloc[0,0] = data.iloc[_trade,3] # update begging price
                    
                df_trade = df_trade.filter(regex='Close')
                df_trade[f'Value-{data.iloc[_trade,0]}'] = (df_trade.iloc[:,0]).astype(float) * float(data.iloc[_trade,2]) #volume bought
                df_trade[f'P/L-{data.iloc[_trade,0]}'] = round((df_trade.iloc[:,0].astype(float) - float(df_trade.iloc[0,0])) / float(df_trade.iloc[0,0]) * 100,2)
                df_trades_all.append(df_trade)
            
            df_trades = pd.concat(df_trades_all, axis=1).replace(np.nan,0).round(2)
            df_trades['Total_value'] = df_trades.filter(regex="Value-").astype(float).sum(axis=1)
            df_trades_length = df_trades.shape[1]

            for index in range(0,len(data)):
                df_trades[f'Percentage_contribution_{data.iloc[index,0]}'] = round(df_trades.filter(regex="Value").iloc[:,index] / df_trades['Total_value'],2)
                df_pl[f'P/L-{data.iloc[index,0]}'] = round(df_trades.filter(regex='P/L').iloc[:,index] * df_trades[f'Percentage_contribution_{data.iloc[index,0]}'],2)
            df_trades['Total_value'] = df_trades['Total_value'].astype(float)
            df_pl['Total-P/L'] = round(df_pl.filter(regex='P/L').astype(float).sum(axis=1))

            # waht to see ->
            # 1 KPI: 
            # Current Value | ATH Value | ATL Value | P/L
            row1 = st.columns(2)
            row2 = st.columns(2)

            KPI_list=[
                [translations["kpi_1"][st.session_state.lang],df_trades['Total_value'].iloc[-1]],
                [translations["kpi_2"][st.session_state.lang],float(df_trades[df_trades['Total_value'] == df_trades.iloc[-30:,:]['Total_value'].max()]['Total_value'])],
                [translations["kpi_3"][st.session_state.lang],float(df_trades[df_trades['Total_value'] == df_trades.iloc[-30:,:]['Total_value'].min()]['Total_value'])],
                [translations["kpi_4"][st.session_state.lang], df_pl.iloc[-1,-1]]
                ]

            for index, col in enumerate(row1 + row2):
                title = col.container(height=120)
                title.metric(KPI_list[index][0], str(round(KPI_list[index][1],2)) + " %" if KPI_list[index][0] == "Profit/Loss" else str(round(KPI_list[index][1],2)))

            # 2. option to see:
            # a) all portoflio all together
            # b) single trades with option on the side to include exclude them
            tab1, tab2 = st.tabs(['Value Gain','P/L'])
            with tab1:
                st.header('Whole portoflio')
                st.line_chart(df_trades['Total_value'])
            with tab2:
                st.header('Profit and Loss')
                radio_selector = st.radio("", ['Portfolio','Single Transactions'], horizontal=True, key="radio_sel")
                if radio_selector == "Portfolio":
                    st.line_chart(df_pl.iloc[:,:-1])
                    #st.line_chart(df_pl[:,-1])
                elif radio_selector == "Single Transactions":
                    st.line_chart(df_pl.iloc[:,-1])
            if "setup_complete" not in st.session_state:
                st.session_state["setup_complete"] = True

            # 4. Table with
            # Ticker | Purchase Date | Quantity | Purchase Price | Latest available Price | P/L | Value_gain
            for index_, trades_ in enumerate(df_trades_all):
                last_table.iloc[index_, 3] = float(trades_.iloc[0,0])
                last_table.iloc[index_,4] = float(trades_.iloc[-1,0])
            last_table['Value Gain'] = (last_table['Latest Available Price'] - last_table['Purchase Price']) * (last_table['Quantity']).astype(float)
            last_table['P/L'] = round(((last_table['Latest Available Price'] - last_table['Purchase Price'])/last_table['Purchase Price']) * 100,2)
            st.dataframe(last_table, hide_index=True)
            st.dataframe(df_trades)
        else:
            #st.dataframe(st.session_state.data, width="stretch", hide_index=True)

            st.data_editor(
                modified_df,
                key="data_editor",
                on_change=callback,
                hide_index=True,
                column_config=column_config,
            )