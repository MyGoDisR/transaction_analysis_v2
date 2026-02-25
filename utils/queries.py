import sqlite3
import pandas as pd
import streamlit as st
from utils import login_management

DB_PATH = "db/users_.db"
SCHEMA_PATH = "db/schema1.sql"

#### Admin Usage ############################################################################

# 0. Clear specific tables
def clear_table(table_name):
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()
    cursor.execute('''
    DELETE FROM table_name 
    ''', (table_name))
    conn.commit()
    conn.close()
    return

# 1. Initialize db
def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=100)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
        
    with open(SCHEMA_PATH, "r") as f:
        sql_script = f.read()
       
    cursor.executescript(sql_script)  # executes multiple statements
    conn.commit()
    conn.close()
    return

# 1.1. Clean Duplicates From Any Table in DB
def clean_duplicates_from_any_table(table_name,conn):

    select_query = f"SELECT * FROM {table_name}"
    df_all = pd.read_sql_query(select_query, conn)
    df_all = df_all.drop_duplicates()

    df_all.to_sql(name=table_name, con=conn, if_exists='replace', index=False)
    conn.close()
    return

#### User Details ############################################################################

# 2.1. Get user login details
def get_user_details():
    conn = sqlite3.connect(DB_PATH, timeout=30)

    # Checking userbase 
    select_query = "SELECT * FROM users;"
    df_users = pd.read_sql_query(select_query, conn)
    conn.close()
    return df_users

# 2.2. Insert data to user table - new user added:
def new_user_to_db(user_choice):
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()

    login_details =[
        st.session_state['login_'],
        login_management.hash_password(st.session_state['pass_'])[1],
        login_management.hash_password(st.session_state['pass_'])[0],
        True if 'T' in user_choice else False,
        True if 'R' in user_choice else False
    ]
        
    cursor.execute('''
        INSERT INTO users (login_, password_, seed, trading, real_estate) 
        VALUES (?,?,?,?,?);
        ''', (login_details))
    conn.commit()
    conn.close()
    return

#### Stock Data ############################################################################

# 3.1. Get user stock info
def get_user_stock(login_):
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()
    cursor.execute('''
    SELECT ticker, purchase_date, quantity, purchase_price
    FROM stock_date
    WHERE login_ = ?
    ''', (login_))
    conn.commit()
    conn.close()
    return

# 3.2. Post user stock info
def post_user_stock(login_, ticker, purchase_date, quantity, purchase_price):
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO stock_data (login_, ticker, purchase_date, quantity, purchase_price):
    VALUES (?,?,?,?)
    ON CONFLICT(login_, ticker, purchase_date, quantity, purchase_price)
    DO UPDATE SET purchase_price = (purchase_price + excluded.purchase_price)/(quantity + excluded.quantity),
    DO UPDATE SET quantity = quantity + excluded.quantity                
    ''', (login_, ticker, purchase_date, quantity, purchase_price))
    # this update sets it to (1) calcaulte weighted average of purchase price, (2) update quantity 
    conn.commit()
    conn.close()
    return

#### Crypto Data ############################################################################

# 4.1. Get user crypto info
def get_user_crypto(login_):
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()
    cursor.execute('''
    SELECT ticker, purchase_date, quantity, purchase_price
    FROM crypto_date
    WHERE login_ = ?
    ''', (login_))
    conn.commit()
    conn.close()
    return

# 4.2. Post user crypto info
def post_user_crypto(login_, ticker, purchase_date, quantity, purchase_price):
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO crypto_data (login_, ticker, purchase_date, quantity, purchase_price):
    VALUES (?,?,?,?)
    ON CONFLICT(login_, ticker, purchase_date, quantity, purchase_price)
    DO UPDATE SET purchase_price = (purchase_price + excluded.purchase_price)/(quantity + excluded.quantity),
    DO UPDATE SET quantity = quantity + excluded.quantity                
    ''', (login_, ticker, purchase_date, quantity, purchase_price))
    # this update sets it to (1) calcaulte weighted average of purchase price, (2) update quantity 
    conn.commit()
    conn.close()
    return

#### Deposit Data ############################################################################

# 5.1. Get user deposit info
def get_user_deposit(login_):
    conn = sqlite3.connect(DB_PATH, timeout=30)
    df = pd.read_sql_query('''SELECT bank, purchase_date, amount, interest_rate, sellout_date 
                           FROM deposit_data
                           WHERE login_ = ?''', conn, params=(login_,))
    conn.close()
    return df

# 5.2. Post user deposit info
def post_user_deposit(login_, df_deposit):
    df_deposit_copy = df_deposit.copy()
    df_deposit_copy['login_'] = login_
    st.write(df_deposit_copy)
    df_deposit_copy.rename(columns={
        'Bank':'bank',
        'Purchase Date':'purchase_date',
        'Amount':'amount',
        'Interest Rate':'interest_rate',
        'Period':'sellout_date'
    }, inplace=True)

    conn = sqlite3.connect(DB_PATH, timeout=30)

    df_deposit_copy.to_sql(name='deposit_data', con=conn, if_exists='append', index=False)

    clean_duplicates_from_any_table('deposit_data',conn)

    conn.close()
    return

#### Bonds Data ############################################################################

# 6.1. Get user bonds info
def get_user_bonds(login_):
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()
    cursor.execute('''
    SELECT country, purchase_date, amount, interest_rate, sellout_date, closed_
    FROM bonds_data
    WHERE login_ = ?
    ''', (login_))
    conn.commit()
    conn.close()
    return

# 6.1. Post user bonds info
def post_user_bonds(login_):
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO bonds_data (country, purchase_date, amount, interest_rate, sellout_date, closed_)
    FROM bonds_data
    WHERE login_ = ?
    ''', (login_))
    conn.commit()
    conn.close()
    return

#### Flats For Sale ############################################################################

# 7.1. Get flats for sale
def get_flats_for_sale():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    df = pd.read_sql_query("SELECT * FROM Flat_for_Sale", conn)
    conn.close()
    return df

# 7.2. Get flats for sale
def post_flats_for_sale(df):
    conn = sqlite3.connect(DB_PATH, timeout=30)
    df.to_sql(name='Flat_for_Sale', con=conn, if_exists='append')
    conn.close()
    return df

#### Transaction Data ############################################################################

# 8.1. Post user transaction info to db
def post_trans_data():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    # getting to all
    processed_files = f'Data/{st.session_state.role_}/Transactions/Processed'
    df_csv = pd.read_csv(f'{processed_files}'+'/final_output.csv')
    # foreign key column for db
    df_csv['login_'] = st.session_state.role_
    df_sql = pd.read_sql_query("SELECT * FROM trans", conn)
    if len(df_sql) == 0:
        df_csv.to_sql(name='trans', con=conn)
    else:
        df_new = pd.concat([df_sql,df_csv]).drop_duplicates(keep=False)
        df_new.to_sql(name='trans', con=conn, if_exists='append')

    conn.close()
    return 

# 8.2. Post user transaction info to db
def get_trans_data():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    df_sql = pd.read_sql_query("SELECT * FROM trans", conn)
    conn.close()
    return df_sql

#### FX RATES ############################################################################

# 9.1 Get Last Available Rates From DB
def get_last_available_price_from_db():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    select_query = f"SELECT * FROM FX_table ORDER BY Date DESC LIMIT 1"
    df_last_fx_rates = pd.read_sql_query(select_query, conn)
    conn.close()
    return df_last_fx_rates

# 9.2 Clean FX Table 
def clean_fx_table():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    select_query = f"SELECT * FROM FX_table"
    df_fx_rates_all = pd.read_sql_query(select_query, conn)
    df_fx_rates_all = df_fx_rates_all.drop_duplicates()

    df_fx_rates_all.to_sql(name='FX_table', con=conn, if_exists='replace', index=False)
    conn.close()
    return

# 9.3 Append newly retrieved FX Rates
def append_to_fx_table(df_with_newly_fx_rates):
    conn = sqlite3.connect(DB_PATH, timeout=30)
    df_with_newly_fx_rates.to_sql(name='FX_table', con=conn, if_exists='append')
    conn.close()
    return