import streamlit as st
import utils.trading as trading
import utils.navigation as navigation
import pandas as pd
import numpy as np
import sqlite3
from  utils import queries as qs
from datetime import datetime as dt

from forex_python.bitcoin import BtcConverter

import yfinance as yf
import pandas_datareader as pdr
import restricted as res_ 

import os
import requests

# Security 
if "role_" not in st.session_state:
    st.switch_page("app.py")

navigation.menu()

st.title("Yahoo Finance Data")

# Creating conection to db
con = qs.get_connection('db/users_.db')
cursor = con.cursor()

df_portfolio = pd.read_sql_query(f"SELECT * FROM user_portfolio WHERE login = ?;", con, params=(st.session_state.role_,))

if df_portfolio.empty:
    st.write('You do not input any trading data yet')
    st.write('')
    st.write('In order to change that please provide:')
    
    if 'data' not in st.session_state:
        data = pd.DataFrame({'Ticker':[],'Purchase Date':[],'Quantity':[],'Purchase Price':[]})
        st.session_state.data = data

    def add_dfForm():
        row = pd.DataFrame({'Ticker':[str.upper(st.session_state.ticker)],
                'Purchase Date':[st.session_state.p_date],
                'Quantity':[st.session_state.quant],
                "Purchase Price":[st.session_state.p_price]})
        
        st.session_state.data = pd.concat([st.session_state.data, row])

    def noadd_dfForm():
        return None

    dfForm = st.form(key='dfForm')
    with dfForm:
        trade = []
        dfColumns = st.columns(4)
        with dfColumns[0]:
            st.text_input('Ticker', key='ticker')
        with dfColumns[1]:
            st.text_input('Purchase Date', key='p_date')
        with dfColumns[2]:
            st.text_input('Volume', key='quant')
        with dfColumns[3]:
            st.text_input('Purchase price', key='p_price')
        i = []
        
        if len(st.session_state.ticker) != 0 and len(st.session_state.ticker) < 10:
            i.append(1)
            trade.append(st.session_state.ticker)
        else:
            st.error('Please provide correct Ticker')
            
        if len(st.session_state.p_date) == 10:
            i.append(2)
            trade.append(st.session_state.p_date)
        else:
            st.error('Please provide correct date format dd/mm/yyyy')

        if len(st.session_state.quant) > 0:
            i.append(3)
            trade.append(st.session_state.quant)
        else:
            st.error('Please provide volume')

        if len(st.session_state.p_price) >= 0:
            i.append(4)
            trade.append(st.session_state.p_price)
        else:
            st.error('''Please provide purchase price, if purchase price wont be within range of Low and High'
                    then autmatically algorithm will assign day close price. If you do not know the price please leave it balnk
            ''')

        st.form_submit_button(on_click=add_dfForm if sum(i) == 10 else noadd_dfForm)

    def save_db():
        new_con = sqlite3.connect("db/users_.db")
        new_cur = new_con.cursor()

        # just in case if overpopulate
        # new_cur.execute('DROP TABLE IF EXISTS user_portfolio;')

        # create new databse if not exsist
        new_cur.execute("""CREATE TABLE IF NOT EXISTS user_portoflio (
                        login TEXT NOT NULL,
                        ticker TEXT NOT NULL,
                        purchase_date DATE,
                        quantity REAL
                        );
                        """)
        portfolio_details =[
            st.session_state.role,
            st.session_state.p_date,
            st.session_state.quant
        ]
        new_cur.execute("Insert Into users (login, purchase_date, quantity) Values(?,?,?);", portfolio_details)

        # just in case if overpopulate
        # new_cur.execute('DROP TABLE IF EXISTS price_history;')

        # create new databse if not exsist
        new_cur.execute("""CREATE TABLE IF NOT EXISTS price_history (
                        ticker TEXT NOT NULL, 
                        purchase_date DATE,
                        close_price REAL,
                        quantity REAL
                        );
                        """)
        portfolio_details =[
            st.session_state.role,
            st.session_state.p_date,
            st.session_state.quant
        ]
        new_cur.execute("Insert Into users (login, purchase_date, quantity) Values(?,?,?);", portfolio_details)

        new_con.commit()
        new_con.close()


    # Change the button to past data to db and the analysis will be shown
    # After pressing the filled form should disappear
    # Show dataframe with just added tickers
    if len(st.session_state.data)>0:
        st.dataframe(st.session_state.data, use_container_width=True, hide_index=True)
        all_t = pd.DataFrame
        if st.button('Show analysis'):         
            df_all_trades = pd.DataFrame()
            df_portfolio = pd.DataFrame()
            df_trades_all = []

            for trade in range(0,len(data)):
                df_trade = yf.download(data.iloc[trade,0],data.iloc[trade,1],dt.today().strftime('%Y-%m-%d'))
            
                if data.iloc[trade,-1] >= df_trade.iloc[0,2] and data.iloc[trade,-1] <= df_trade.iloc[0,1]:
                    df_trade.iloc[0,0] = data.iloc[trade,-1]
                
                df_trade = df_trade.loc[:,['Close']]
                df_trade[f'Value-{data.iloc[trade,0]}'] = df_trade['Close'] * data.iloc[trade,2] #volume
                df_trade[f'P/L - {data.iloc[trade,0]}'] = round((df_trade['Close'] - float(df_trade['Close'].iloc[0])) / float(df_trade['Close'].iloc[0]) * 100,2)
                df_trade.rename(columns={'Close': f'{data.iloc[trade,0]}-Close'}, inplace=True)
            
            df_trades_all.append(df_trade)
            df_trades = pd.concat(df_trades_all, axis=1).replace(np.nan,0).round(2)
            value_invest = [col for col in df_trades.columns if 'Value' in col]
            df_trades['Total_value'] = df_trades.loc[:,value_invest].astype(float).sum(axis=1)
            df_trades_length = df_trades.shape[1]
            df_pl = pd.DataFrame()
            for i in range(0,df_trades['Value_of_invest'].shape[1]):
                df_trades[f'Percentage_contribution_{i}'] = round(df_trades['Value_of_invest'].iloc[:,i] / df_trades['Total_value'],2)
                df_pl[f'P/L_{i}'] = round(df_trades['P/L'].iloc[:,i] * df_trades[f'Percentage_contribution_{i}'],2)
            
            #df_trades = df_trades.iloc[2:,:]
            df_trades['Price'] = pd.to_datetime(df_trades['Price'])
            df_trades.rename(columns={'Price':"Date"}, inplace=True)
            df_trades['Total_value'] = df_trades['Total_value'].astype(float)
            df_trades.set_index(df_trades['Date'], inplace=True)
            df_trades = df_trades.iloc[:,1:]

            df_pl['Date'] = pd.to_datetime(df_pl['Date'])
            df_pl.set_index(df_pl['Date'], inplace=True)
            df_pl = -df_pl.iloc[:,1:]

            value_invest = [col for col in df_trades.columns if 'Value' in col]
            df_all_trades = df_trades.loc[:,value_invest].astype(float)

            # waht to see ->
            # 1 KPI:
            # Current Value | ATH Value | ATL Value | P/L
            row1 = st.columns(2)
            row2 = st.columns(2)

            KPI_list=[
                ["Total Portoflio Value",df_trades.iloc[-1,:]['Total_value']],
                ["ATH (last 30 days)",float(df_trades[df_trades['Total_value'] == df_trades.iloc[-30:,:]['Total_value'].max()]['Total_value'])],
                ["ATL (last 30 days)",float(df_trades[df_trades['Total_value'] == df_trades.iloc[-30:,:]['Total_value'].min()]['Total_value'])],
                ["Profit/Loss", df_pl.iloc[-1,1:].sum()]
                ]

            for index, col in enumerate(row1 + row2):
                title = col.container(height=120)
                title.metric(KPI_list[index][0], str(round(KPI_list[index][1],2)))

            # 2. option to see:
            # a) all portoflio all together
            # b) single trades with option on the side to include exclude them
            tab1, tab2, tab3 = st.tabs(['Portfolio','Trades separelty','P/L'])
            with tab1:
                st.header('Whole portoflio')
                st.line_chart(df_trades['Total_value'])
                # need to include 
                #st.dataframe(st.session_state.data, use_container_width=True, hide_index=True)
            with tab2:
                st.header('Single trades')
                st.line_chart(df_all_trades)
            with tab3:
                st.header('Profit and Loss')
                st.line_chart(df_pl)
            
            df_trades_data = pd.DataFrame({"Ticker":df_all_trades.columns,"Included":True})
            st.write(df_trades_data)
            #st.data_editor(df_all_trades.)
            categories = st.multiselect('Tickers', options=df_all_trades.columns, default=df_all_trades.columns)
            dfColumns = st.columns(2)
            with dfColumns[0]:
                st.text_input('Ticker')
            with dfColumns[1]:
                st.line_chart(df_all_trades)

            # 4. Table with
            # Ticker | Purchase Date | Quantity | Purchase Price | Latest available Price | P/L | Value_gain
            data = pd.DataFrame({'Ticker':['BNB-USD','BTC-USD'],'Purchase Date':["2025-07-25","2024-09-25"],'Quantity':[0.55, 0.01],'Purchase Price':[np.nan,np.nan]})
            st.write(df_trades)