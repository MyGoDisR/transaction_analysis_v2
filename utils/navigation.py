import streamlit as st
from datetime import datetime
from time import sleep
import pandas as pd
import sqlite3
import abalin_nameday
import requests
from urllib3 import HTTPSConnectionPool

try:
    response = requests.get('https://nameday.abalin.net/api/V2/today/Warsaw', params={'data': 'pl'})
    names_days_today = response.json()['data']['pl']
except:
    response = 'No'
    names_days_today = 'No internet connection'
#names_days_today ='None'

def authenticated_menu():
    if 'lang' not in st.session_state:
        st.session_state.lang = "ENG"

    translations = {
    "sidebar": {"ENG": "Navigation Sidebar", "POL": "Panel Sterujący"},
    "home": {"ENG": "Home", "POL": "Start"},
    "profile": {"ENG": "Your Profile", "POL": "Twój Profil"},
    "first_page": {"ENG": "Financial Yearly", "POL": "Finanse Roczne"},
    "second_page": {"ENG": "Finance Monthly", "POL": "Finanse w ujęciu miesięcznym"},
    "third_page": {"ENG": "Real estate", "POL": "Nieruchomości"},
    "fourth_page": {"ENG": "Trading", "POL": "Inwestowanie"},
    "welcome": {"ENG": "Welcome,", "POL": "Witaj, "},
    "today": {"ENG": "Today is: ", "POL": "Dziś jest: "},
    "name_days": {"ENG":"Today name days have:", "POL":"Dziś imieniny mają:"},
    "language": {"ENG": "Choose language", "POL": "Wybierz język"},
    "loggout": {"ENG": "Logg out", "POL": "Wyloguj się"},
    }

    with st.sidebar:
        st.title(translations["sidebar"][st.session_state.lang])
        st.page_link(f"pages/home.py", label=translations["home"][st.session_state.lang], icon="🏡")
        st.divider()
        st.subheader(translations["profile"][st.session_state.lang])
        st.page_link(f"pages/yearly.py", label=translations["first_page"][st.session_state.lang])
        st.page_link(f"pages/monthly.py", label=translations["second_page"][st.session_state.lang])

        # Creating conection to db
        conn = sqlite3.connect("db/users_.db")

        # Checking userbase 
        select_query = f"SELECT * FROM users WHERE login_='{st.session_state.role_}';"
        df_users = pd.read_sql_query(select_query, conn)

        if df_users['real_estate'].iloc[0] == 1:
            
            st.page_link(f"pages/real_estates.py", label=translations["third_page"][st.session_state.lang])
        if df_users['trading'].iloc[0] == 1:
            st.page_link(f"pages/trading_v2.py", label=translations["fourth_page"][st.session_state.lang])
    
        st.divider()
        st.write(translations["welcome"][st.session_state.lang] + " " + st.session_state['role_'] + "!")
        st.write(translations["today"][st.session_state.lang] + "  " + datetime.today().strftime("%Y-%m-%d"))
        st.write(translations["name_days"][st.session_state.lang])
        st.write(names_days_today)
        st.divider()
        
        def set_lang(lang_code):
            st.session_state.lang = lang_code
        st.button("English", on_click=set_lang, args=("ENG",))
        st.button("Polski", on_click=set_lang, args=("POL",))
        st.divider()
        st.write("")
        st.write("")
        st.page_link("app.py", label=translations["loggout"][st.session_state.lang])

        conn.close()
        return st.session_state.lang

def unauthenticated_menu():
    st.sidebar.title('Use below link to log in or register:')
    st.sidebar.page_link("app.py", label="Log in / Sign in")


def menu():
    if "role_" not in st.session_state or st.session_state.role_ is None:
        unauthenticated_menu()
        return
    authenticated_menu()


def logout():
    st.session_state.logged_in = False
    st.info("Logged out successfully!")
    sleep(0.5)
    st.switch_page("app.py")