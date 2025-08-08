CREATE TABLE IF NOT EXSIST users (
    login_ TEXT NOT NULL, 
    password_, 
    seed INTEGER,
    trading BLOB,
    flats BLOB,
    land BLOB,
    house BLOB,
    last_refresh DATE 
);

CREATE TABLE IF NOT EXSIST user_portfolio (
    login_ TEXT NOT NULL,
    ticker TEXT NOT NULL,
    purchase_date DATE,
    quantity REAL,
    PRIMARY KEY (login_, ticker, purchase_date)
    FOREIGN KEY (login_) REFERENCES users(login_)
);

CREATE TABLE IF NOT EXSIST price_history (
    ticker TEXT,
    data_ DATE,
    close_price REAL,
    PRIMARY KEY (symbol, data_)
);