from core.common import *

# Security 
if "role_" not in st.session_state:
    st.switch_page("app.py")

# Language chosen
if 'lang' not in st.session_state:
    st.session_state.lang = "ENG"

# Navigation applied
# As of now users have option what to see in the navigation panel
# that is chosen at the registration form
navigation.menu()

# Dictionary with translations for the app, in order to make it multilingual
translations = {
    "title": {"ENG": "Hello", "POL": "Witaj"},
    "put_data": {"ENG": "In this tab you can put your data", "POL": "Tutaj możesz załączyć swoje pliki"},
    "process_info": {"ENG": "Please bear in mind that as of now we are able to process ipko, mbank, santander and bnp pdf bank statements", "POL": "Algorytm jest w stanie przeprocesować IPKO, mBank, Santander, BNP Paribas"},
    "naming_info": {"ENG": "Please bear in mind that in order to see your data from excel please name your columns as follow 'Date', 'Amount', 'Run_balance','Desc','Trans. type'", "POL": "Jeżeli załączac swoje dane Excel prosze nazwij kolumny: 'Date', 'Amount', 'Run_balance','Desc','Trans. type'"},
    "choose_file_": {"ENG": "Choose a CSV or PDF file", "POL": "Wybierz pliki CSV albo PDF"},
    "type_mess": {"ENG": "App does not support other file types then pdf and csv", "POL": "Aplikacja nie wspiera pliki innego typu niż csv i pdf"}
    }

# Main page of the app, where users can upload their financial/banking statements and see the results
st.title(translations["title"][st.session_state.lang] + " " + st.session_state.role_ + " !")
st.write(translations["put_data"][st.session_state.lang])
st.write(translations["process_info"][st.session_state.lang])
st.write(translations["naming_info"][st.session_state.lang])
st.write("")

# Process the uploaded file
uploaded_files = st.file_uploader(
    translations["choose_file_"][st.session_state.lang], accept_multiple_files=True
)
for uploaded_file in uploaded_files:
    suffix = uploaded_file.name.split('.')[-1]
    if suffix == 'csv':
        finance.streamlit_uploaded_file(uploaded_file)
        finance.csv_user_load()
        # to store in the sql 
    elif suffix == 'pdf':
        finance.streamlit_uploaded_file(uploaded_file)
        finance.data_to_df()
    else:
        st.write(translations["type_mess"][st.session_state.lang])