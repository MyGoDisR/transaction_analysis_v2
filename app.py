import streamlit as st
from time import sleep
import navigation

import sqlite3
import pandas as pd
import certifi

# This is the structure of the app,
# There will be a navigation bar in for historical spenditure by year/month/week and overall
# To do:
# 3. Add new subsector Finance this includes: 
# - historical loan, 
# - api calls to market data (probably yahoo finance),
# - house cost - this has to be on request due to efficiency
# - land cost - this has to be on request due to efficiency
# - appartments for rent 
# 4. Exchange rate should be store in db so that if not avialable then max of

# Initialize st.session_state.lang to None
if "lang" not in st.session_state:
    st.session_state.lang = 'ENG'
    lang_number = 0

lang = ["ENG", "POL"]
lang_selection = st.pills("", lang, selection_mode="single", width="stretch")
st.session_state.lang = 'ENG' if None == lang_selection else lang_selection

translations = {
    "title": {"ENG": "Welcome to Finance app", "POL": "Witam w apliacji Analiza budżetu"},
    "logs": {"ENG": "Username", "POL": "Login"},
    "pass": {"ENG": "Password", "POL": "Hasło"},
    "login": {"ENG": "Log in", "POL": "Zaloguj"},
    "new_prof": {"ENG": "Do you want to create a new profile?", "POL": "Czy chcesz stworzyć nowe konto?"},
    "yes_": {"ENG": "Yes", "POL": "Tak"},
    "no_": {"ENG": "No", "POL": "Nie"},
    "success_login": {"ENG":"Logged in successfully!", "POL": "Zalogowano się pomyślnie!"},
    "no_login": {"ENG":"Wrong password! Try once again ;)", "POL": "Nie poprawne hasło spróbuj ponownie ;)"},
    "noexsist_login": {"ENG":"The profile with this username does not exsist!", "POL": "Profil z takim loginem nie istnieje!"}
}

# Initialize st.session_state.role to None
if "role" not in st.session_state:
    st.session_state.role = None

if st.session_state.get('creat_new_account'):
    st.session_state['name'] = 'new'
if st.session_state.get('no_new_account'):
    st.session_state['name'] = 'no_new'

if "clicked" not in st.session_state:
    st.session_state["clicked"] = False
    
def onSearch(opt):
    st.session_state["clicked"] = True


st.title(translations["title"][st.session_state.lang])

username = st.text_input(translations["logs"][st.session_state.lang], key='login_')
password = st.text_input(translations["pass"][st.session_state.lang], key='password', type="password")

# Creating conection to db
new_con = sqlite3.connect("users_.db")
new_cur = new_con.cursor()

# Checking userbase 
select_query = "SELECT * FROM users;"
df_users = pd.read_sql_query(select_query, new_con)

if st.button(translations["login"][st.session_state.lang], type="primary"):
    import utils.login_management as login_management
    if username in df_users['login'].tolist():
        if login_management.hash_password(password)[1] == df_users[df_users['login']==f'{username}']['password'].iloc[0]:
            new_cur.close()
            st.session_state.logged_in = True
            st.session_state.role_ = st.session_state['login_']
            key = "_role"
            st.session_state.logged_in = True
            st.success(translations["success_login"][st.session_state.lang])
            sleep(0.5)
            navigation.menu()
            st.switch_page("pages/home.py")
        else:
            st.error(translations["no_login"][st.session_state.lang])
    else:
        st.error(translations["noexsist_login"][st.session_state.lang])

st.write('')
st.write('')
st.write(translations["new_prof"][st.session_state.lang])
col1, col2 = st.columns([1,2])
with col1:
    if st.button(translations["yes_"][st.session_state
.lang]):
        st.switch_page("pages/new_user.py")
with col2:
    if st.button(translations["no_"][st.session_state
.lang]):
        st.switch_page("pages/home.py")