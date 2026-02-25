CREATE TABLE IF NOT EXISTS users (
    login_ TEXT NOT NULL PRIMARY KEY,
    password_ TEXT NOT NULL,
    seed INTEGER,
    trading INTEGER,
    real_estate INTEGER
);

CREATE TABLE IF NOT EXISTS stock_data (
    login_ TEXT NOT NULL,
    ticker TEXT,
    purchase_date DATE,
    purchase_price REAL,
    quantity REAL,
    sellout_date DATE,
    profit_or_loss REAL,
    closed_ INTEGER,
    FOREIGN KEY (login_) REFERENCES (login_)
);

CREATE TABLE IF NOT EXISTS bonds_data (
    login_ TEXT NOT NULL,
    country TEXT NOT NULL,
    purchase_date DATE,
    amount REAL,
    interest_rate REAL,
    sellout_date DATE,
    closed_ INTEGER,
    FOREIGN KEY (login_) REFERENCES (login_)
);

CREATE TABLE IF NOT EXISTS deposit_data (
    login_ TEXT NOT NULL,
    bank TEXT NOT NULL,
    purchase_date DATE,
    amount REAL,
    interest_rate REAL,
    sellout_date DATE,
    closed_ INTEGER,
    FOREIGN KEY (login_) REFERENCES (login_)
);

CREATE TABLE IF NOT EXISTS crypto_data (
    login_ TEXT NOT NULL,
    ticker TEXT,
    purchase_date DATE,
    purchase_price REAL,
    quantity REAL,
    sellout_date DATE,
    profit_or_loss REAL,
    closed_ INTEGER,
    FOREIGN KEY (login_) REFERENCES (login_)
);

CREATE TABLE IF NOT EXISTS trans (
    login_ TEXT NOT NULL,
    Date DATE,
    Desc TEXT,
    Run_balance REAL,
    Amount REAL,
    Tags TEXT,
    FOREIGN KEY (login_) REFERENCES (login_)
);

CREATE TABLE IF NOT EXISTS FX_table (
    PLN_EUR REAL,
    PLN_USD REAL,
    Date DATE
);