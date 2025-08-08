import sqlite3

# 0. Connect to database
def get_connection(db_path="db/users_.db"):
    return sqlite3.connect(db_path)

# 1. Get user portfolio info
def get_user_portfolio(conn, login_):
    cursor = conn.cursor()
    cursor.execute('''
    SELECT ticker, purchase_date, quantity
    FROM user_portoflio
    WHERE login_ = ?
    ''', (login_))
    return cursor.fetchall()

# 2. Insert trade to user portfolio
def insert_trade(conn, login_, ticker, purchase_date, quantity):
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO user_portfolio (login_, ticker, purchase_date, quantity):
    VALUES (?,?,?,?)
    ON CONFLICT(login_, ticker, purchase_date, quantity)
    DO UPDATE SET quantity = quantity + excluded.quantity 
    ''', (login_, ticker, purchase_date, quantity))
    return cursor.fetchall()

# 3. Get new retreieve data to db
def insert_data_to_db(conn, ticker, date_, close_price):
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO price_history (ticker, date_, close_price):
    VALUES (?,?,?)
    ''', (ticker, date_, close_price))
    return cursor.fetchall()