# Libraries
import streamlit as st
import utils.web_scrap as webscrap
import navigation

# Security 
if "role_" not in st.session_state:
    st.switch_page("app.py")

navigation.menu()

st.write("In progress")