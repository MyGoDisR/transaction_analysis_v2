from datetime import datetime
import yfinance as yf

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

import restricted as rest

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

def get_crypto_data(ticker):
  url = 'https://sandbox-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
  parameters = {
    'slug':ticker,
    'convert':'USD'
  }

  headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': rest.key,
  }

  session = Session()
  session.headers.update(headers)

  response = session.get(url, params=parameters)
  print(json.load(response.text)['data']['1']['quote']['USD'])