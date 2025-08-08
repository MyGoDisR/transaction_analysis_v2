import streamlit as st
import utils.trading as trading
import navigation
import pandas as pd
import numpy as np
import sqlite3
from  db import queries as qs

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
new_con = qs.get_connection()
new_cur = new_con.cursor()

# just in case if overpopulate
# new_cur.execute('DROP TABLE IF EXISTS user_;')

# create new databse if not exsist
new_cur.execute("""CREATE TABLE IF NOT EXISTS user_portfolio (
                    id INTEGER,
                    login TEXT 
                    portoflio_id INTEGER,
                    purchase_date NUMERIC,
                    purchase_price NUMERIC
                    );
                    """)

new_cur.execute("""CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER, 
                    ticker BLOB, 
                    date NUMERIC,
                    close NUMERIC,
                    volume INTEGER 
                    );
                    """)



df_portfolio = pd.read_sql_query(f"SELECT * FROM user_portfolio WHERE login = ?;", new_con, params=(st.session_state.role_,))

if df_portfolio.empty:
    st.write('You do not input any trading data yet')
    st.write('')
    st.write('In order to change that please provide:')
    
    if 'data' not in st.session_state:
        data = pd.DataFrame({'Ticker':[],'Purchase Date':[],'Quantity':[]})
        st.session_state.data = data

        new_con.commit()
        new_con.close()

    def add_dfForm():
        row = pd.DataFrame({'Ticker':[str.upper(st.session_state.ticker)],
                'Purchase Date':[st.session_state.p_date],
                'Quantity':[st.session_state.quant]})
        st.session_state.data = pd.concat([st.session_state.data, row])

    def noadd_dfForm():
        return None

    dfForm = st.form(key='dfForm')
    with dfForm:
        dfColumns = st.columns(3)
        with dfColumns[0]:
            st.text_input('Ticker', key='ticker')
        with dfColumns[1]:
            st.text_input('Purchase Date (dd/mm/yyyy)', key='p_date')
        with dfColumns[2]:
            st.text_input('Quantity', key='quant')
        i = []
        
        if len(st.session_state.ticker) != 0 and len(st.session_state.ticker) < 6:
            i.append(1)
        if len(st.session_state.p_date) == 10:
            i.append(2)
        if len(st.session_state.quant) > 0:
            i.append(3)

        st.form_submit_button(on_click=add_dfForm if sum(i) == 6 else noadd_dfForm)

    def save_db():
        new_con = sqlite3.connect("users_.db")
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



    # Show dataframe with just added tickers
    data = st.session_state.data
    if len(data)>0:
        st.dataframe(data, use_container_width=True, hide_index=True)

        st.button('Show analysis')
