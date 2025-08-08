import random
import hashlib
import streamlit as st
import sqlite3
import os
import utils.login_management as login_management

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
    if st.session_state['pass_'] != st.session_state['re_pass_']:
        st.error('Password is not the same in both field')
    elif st.session_state['login_'] in os.listdir('Data'):
        st.error('This login already exsist try different name')
    else:
        # Creating conection to db
        new_con = sqlite3.connect("users_.db")
        new_cur = new_con.cursor()

        # just in case if overpopulate
        # new_cur.execute('DROP TABLE IF EXISTS users;')

        # create new databse if not exsist
        new_cur.execute("""CREATE TABLE IF NOT EXISTS users (
                    login TEXT NOT NULL, 
                    password, 
                    seed INTEGER,
                    trading BLOB,
                    flats BLOB,
                    land BLOB,
                    house BLOB,
                    last_refresh DATE 
                    );
                    """)
        login_details =[
            st.session_state['login_'],
            login_management.hash_password(st.session_state['pass_'])[1],
            login_management.hash_password(st.session_state['pass_'])[0],
            True if 'T' in user_choice else False,
            True if 'F' in user_choice else False,
            True if 'L' in user_choice else False,
            True if 'H' in user_choice else False
        ]
        new_cur.execute("Insert Into users (login, password, seed, trading, flats, land, house) Values(?,?,?,?,?,?,?);", login_details)

        # commit insert
        new_con.commit()
        # close the connection
        new_con.close()
        # Create folder for User data
        os.mkdir(f"Data/{st.session_state['login_']}")
        # Create sub-folders Archived and Processed data
        os.mkdir(f"Data/{st.session_state['login_']}/Loaded")
        os.mkdir(f"Data/{st.session_state['login_']}/Processed")
        # notify user about succesfull profile creation
        st.write('New user succesfully created!')

#### Initialize db schema ###
def init_db_from_file(conn, schema_path="db/schema.sql"):
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())