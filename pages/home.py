import streamlit as st
import navigation
import os
import utils.finance as finance

# Security 
if "role_" not in st.session_state:
    st.switch_page("app.py")

if 'lang' not in st.session_state:
    st.session_state.lang = "ENG"

navigation.menu()

translations = {
    "title": {"ENG": "Hello", "POL": "Witaj"},
    "put_data": {"ENG": "In this tab you can put your data", "POL": "Tutaj możesz załączyć swoje pliki"},
    "process_info": {"ENG": "Please bear in mind that as of now we are able to process ipko, mbank, santander and bnp pdf bank statements", "POL": "Algorytm jest w stanie przeprocesować IPKO, mBank, Santander, BNP Paribas"},
    "naming_info": {"ENG": "Please bear in mind that in order to see your data from excel please name your columns as follow 'Date', 'Amount', 'Run_balance','Desc','Trans. type'", "POL": "Jeżeli załączac swoje dane Excel prosze nazwij kolumny: 'Date', 'Amount', 'Run_balance','Desc','Trans. type'"},
    "choose_file_": {"ENG": "Choose a CSV or PDF file", "POL": "Wybierz pliki CSV albo PDF"},
    "type_mess": {"ENG": "we do not support other file types then pdf and csv", "POL": "aplikacja nie wspiera pliki innego typu niż csv i pdf"}
    }

st.title(f"{translations["title"][st.session_state.lang]} {st.session_state.role_}!")
st.write(translations["put_data"][st.session_state.lang])
st.write(translations["process_info"][st.session_state.lang])
st.write(translations["naming_info"][st.session_state.lang])
st.write("")

uploaded_files = st.file_uploader(
    translations["choose_file_"][st.session_state.lang], accept_multiple_files=True
)
for uploaded_file in uploaded_files:
    suffix = uploaded_file.name.split('.')[-1]
    if suffix == 'csv':
        finance.streamlit_uploaded_file(uploaded_file)
        finance.csv_user_load()
    elif suffix == 'pdf':
        finance.streamlit_uploaded_file(uploaded_file)
        finance.data_to_df()
    else:
        st.write(translations["type_mess"][st.session_state.lang])