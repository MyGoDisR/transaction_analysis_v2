import sqlite3
import streamlit as st
from utils import login_management


db_path = "db/users_.db"
schema_path = "db/schema.sql"

##################################################################################################### Admin Usage

# 0. Clear specific tables
def clear_table(table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    DELETE FROM table_name 
    ''', (table_name))
    return cursor.fetchall()

##################################################################################################### Regular Usage

# 0. Connect to database
def get_connection(db_path):
    return sqlite3.connect(db_path)

# 1. Initialize db
def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    with open(schema_path, "r") as f:
        sql_script = f.read()
    
    cursor.executescript(sql_script)  # executes multiple statements
    conn.commit()
    conn.close()

# 2. Get user portfolio info
def get_user_portfolio(conn, login_):
    cursor = conn.cursor()
    cursor.execute('''
    SELECT ticker, purchase_date, quantity
    FROM user_portoflio
    WHERE login_ = ?
    ''', (login_))
    return cursor.fetchall()

# 3. Insert trade to user portfolio
def insert_trade(conn, login_, ticker, purchase_date, quantity):
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO user_portfolio (login_, ticker, purchase_date, quantity):
    VALUES (?,?,?,?)
    ON CONFLICT(login_, ticker, purchase_date, quantity)
    DO UPDATE SET quantity = quantity + excluded.quantity 
    ''', (login_, ticker, purchase_date, quantity))
    return cursor.fetchall()

# 4. Get new retreieve data to db
def insert_data_to_db(conn, ticker, date_, close_price):
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO price_history (ticker, date_, close_price):
    VALUES (?,?,?)
    ''', (ticker, date_, close_price))
    return cursor.fetchall()

# 5. Insert data to user table - new user added:
def new_user_to_db(user_choice):
    conn = sqlite3.connect("db/users_.db")
    cursor = conn.cursor()

    login_details =[
        st.session_state['login_'],
        login_management.hash_password(st.session_state['pass_'])[1],
        login_management.hash_password(st.session_state['pass_'])[0],
        True if 'T' in user_choice else False,
        True if 'F' in user_choice else False,
        True if 'L' in user_choice else False,
        True if 'H' in user_choice else False
    ]
    
    cursor.execute('''
        INSERT INTO users (login_, password_, seed, trading, flats, land, house) 
        VALUES (?,?,?,?,?,?,?);
        ''', (login_details))
    return cursor.fetchall()