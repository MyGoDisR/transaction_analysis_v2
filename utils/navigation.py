import streamlit as st
from datetime import datetime
from time import sleep
import pandas as pd
import sqlite3

def authenticated_menu():
    if 'lang' not in st.session_state:
        st.session_state.lang = "ENG"

    translations = {
    "sidebar": {"ENG": "Navigation Sidebar", "POL": "Panel Sterujący"},
    "home": {"ENG": "Home", "POL": "Start"},
    "profile": {"ENG": "Your Profile", "POL": "Twój Profil"},
    "first_page": {"ENG": "Financial Yearly", "POL": "Finanse Roczne"},
    "second_page": {"ENG": "Creat a New User", "POL": "Finanse w ujęciu miesięcznym"},
    "third_page": {"ENG": "Flat for rent", "POL": "Mieszkania - wynajem"},
    "fourth_page": {"ENG": "Trading", "POL": "Inwestowanie"},
    "fifth_page": {"ENG": "House for sale", "POL": "Dom - kupno"},
    "sixth_page": {"ENG": "Land for sale", "POL": "Działka - kupno"},
    "welcome": {"ENG": "'Welcome,", "POL": "Witaj, "},
    "today": {"ENG": "Today is:", "POL": "Dziś jest: "},
    "refresh": {"ENG": "Last Refresh", "POL": "Ostatnie odświeżenie: "},
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
        new_con = sqlite3.connect("db/users_.db")
        new_cur = new_con.cursor()

        # Checking userbase 
        select_query = f"SELECT * FROM users WHERE login_='{st.session_state.role_}';"
        df_users = pd.read_sql_query(select_query, new_con)

        if df_users['flats'].iloc[0] == 1:
            
            st.page_link(f"pages/flat_for_rent.py", label=translations["third_page"][st.session_state.lang])
        if df_users['trading'].iloc[0] == 1:
            st.page_link(f"pages/trading.py", label=translations["fourth_page"][st.session_state.lang])
        if df_users['house'].iloc[0] == 1:
            st.page_link(f"pages/house.py", label=translations["fifth_page"][st.session_state.lang])
        if df_users['land'].iloc[0] == 1:
            st.page_link(f"pages/land.py", label=translations["sixth_page"][st.session_state.lang]) 
    
        st.divider()
        st.write(f"  {translations["welcome"][st.session_state.lang]} {st.session_state['role_']}!")
        st.write(f'  {translations["today"][st.session_state.lang]} {datetime.today().strftime("%Y-%m-%d")}')
        st.write(f'  {translations["refresh"][st.session_state.lang]} TBD')
        st.divider()
        def set_lang(lang_code):
            st.session_state.lang = lang_code
        st.button("English", on_click=set_lang, args=("ENG",))
        st.button("Polski", on_click=set_lang, args=("POL",))
        st.divider()
        st.write("")
        st.write("")
        st.page_link("app.py", label=translations["loggout"][st.session_state.lang])

        new_cur.close()
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