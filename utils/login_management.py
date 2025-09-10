import random
import hashlib
import streamlit as st
import sqlite3
import os
import utils.login_management as login_management
from utils import queries as qs

#### Password Managment #################################################################################################################################################

def hash_password(password):
  random_int = random.randint(0,100)
  #salt = os.urandom(random_int)  
  password_hash = hashlib.sha256(password.encode())  
  return [random_int, password_hash.digest()] 
 
def encode_hash_pass(password):
    #salt = os.urandom(0)  
    password_hash = hashlib.sha256(password.encode())  
    return password_hash.digest()

#### New user creation ##################################################################################################################################################

def creat_new_user(user_choice):
    if 'lang' not in st.session_state:
        st.session_state.lang = "ENG"

    translations = {
    "error_pass1": {"ENG": "Password should have at least 8 characters", "POL": "Hasło powinno posiadać co najmiej 8 znaków"},
    "error_pass2": {"ENG": "Password is not the same in both field", "POL": "Hasła nie są takie same"},
    "error_login": {"ENG": "This login already exsist - try different name", "POL": "Taki login już istnieje - spróbuj inną nazwe"},
    "error_pass3": {"ENG": "The password should contain at least one number and one special character", "POL": "Hasło powinno zawierać co najmniej jedną liczbe oraz jeden znak specjalny"},
    "succ1": {"ENG": "New user succesfully created!", "POL":"Nowe konto zostało utworzone!"}
    }

    if st.session_state['login_'] in os.listdir('Data'):
        st.error(translations["error_login"][st.session_state.lang])
        return False
    elif len(st.session_state['pass_']) <= 7:
        st.error(translations["error_pass1"][st.session_state.lang])
        return False
    elif st.session_state['pass_'] != st.session_state['re_pass_']:
        st.error(translations["error_pass2"][st.session_state.lang])
        return False
    elif any(not c.isalnum() for c in st.session_state['pass_']) == False or any(i.isdigit for i in st.session_state['pass_']) == False:
        st.error(translations["error_pass3"][st.session_state.lang])
        return False
    else:
        qs.new_user_to_db(user_choice)
        # Create folder for User data
        os.mkdir(f"Data/{st.session_state['login_']}")
        # Create sub-folders Archived and Processed data
        os.mkdir(f"Data/{st.session_state['login_']}/Loaded")
        os.mkdir(f"Data/{st.session_state['login_']}/Processed")
        # notify user about succesfull profile creation
        st.write('New user succesfully created!')
        return True

#### Initialize db schema ###
def init_db_from_file(conn, schema_path="db/schema.sql"):
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())