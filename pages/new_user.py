import streamlit as st
from time import sleep
import os
import sqlite3
import utils.login_management as login_management
import pandas as pd

if "lang" not in st.session_state:
    st.session_state.lang = 'ENG'
    lang_number = 0

lang = ["ENG", "POL"]
lang_selection = st.pills("", lang, selection_mode="single", width="stretch")
st.session_state.lang = 'ENG' if None == lang_selection else lang_selection

if st.session_state.lang == "ENG":
    lang_number = 0
elif st.session_state.lang == "POL":
    lang_number = 1

translations = {
    "new_user": {"ENG": "Creat a New User", "POL": "Stwórz nowy profil"},
    "logs": {"ENG": "Username", "POL": "Login"},
    "pass": {"ENG": "Password", "POL": "Hasło"},
    "repass": {"ENG": "Repeat password", "POL": "Powtórz hasło"},
    "which_page": {"ENG": "Please check which pages you would like to include:", "POL": "LogZaznacz jakie strony chcesz mieć:in"},
    "page_1": {"ENG": "Trading", "POL": "Inwestowanie"},
    "page_2": {"ENG": "Flats for rent", "POL": "Mieszkanie na wynajem"},
    "page_3": {"ENG": "Lands for sale", "POL": "Działka na sprzedaż"},
    "page_4": {"ENG": "House for sale", "POL": "Dom na sprzedaż"},
    "create": {"ENG": "Create", "POL": "Stwórz"},
    "abort": {"ENG": "Abort", "POL": "Wróc do okna logowania"}
}

st.title(translations["new_user"][st.session_state.lang])

left, middle, right = st.columns(3)
left.text_input(translations["logs"][st.session_state.lang], key='login_')
middle.text_input(translations["pass"][st.session_state.lang], key='pass_', type='password')
right.text_input(translations["repass"][st.session_state.lang], key='re_pass_', type='password')

st.write('')
st.write('')
st.write('')
st.write(translations["which_page"][st.session_state.lang])
Trading = st.checkbox(translations["page_1"][st.session_state.lang])
Flat_for_rent = st.checkbox(translations["page_2"][st.session_state.lang])
Land = st.checkbox(translations["page_3"][st.session_state.lang])
House_for_sale = st.checkbox(translations["page_4"][st.session_state.lang])

user_choice = []

if Trading:
    user_choice.append('T')
if Flat_for_rent:
    user_choice.append('F')
if Land:
    user_choice.append('L')
if House_for_sale:
    user_choice.append('H')

st.write('')
st.write('')
st.write('')

col1, col2 = st.columns([1,2])
with col1:
    if st.button(translations["create"][st.session_state.lang]):#, on_click=login_management.creat_new_user(user_choice)):
        if login_management.creat_new_user(user_choice) == True:
            st.session_state.logged_in = True
            st.session_state.role_ = st.session_state['login_']
            sleep(1)
            st.switch_page('app.py')
with col2:
    if st.button(translations["abort"][st.session_state.lang]):
        st.session_state.logged_in = False
        st.switch_page('app.py')