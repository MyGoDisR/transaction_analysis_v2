from datetime import datetime
import yfinance as yf

def trading_yfin(tickers, start_date, end_date):
  data = yf.download(tickers, start_date, end_date)
  return data['Adj Close']

def trading_yfin_2(ticker_symbol, start_date, end_date):
  start_date_ = datetime.strptime(start_date, '%Y-%m-%d')
  end_date_ = datetime.strptime(end_date, '%Y-%m-%d')
  ticker = yf.Ticker(ticker_symbol)
  data = ticker.history(start=start_date_, end=end_date_)
  data.to_csv('lol.csv')
  return data['Adj Close']