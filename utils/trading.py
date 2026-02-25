from datetime import datetime
import yfinance as yf
import streamlit as st

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import os

import pandas as pd
import restricted as rest
import time

def streamlit_uploaded_file_trading(uploaded_file):
    with open(os.path.join(f"Data/{st.session_state.role_}/Trading/Loaded",uploaded_file.name),"wb") as f:
        f.write(uploaded_file.getbuffer())
    alert = st.success("File Saved")
    time.sleep(3)
    alert.empty()


def trading_data_to_analysis():
  folder_path = f'Data/{st.session_state.role_}/Trading'

  path_to_user_loaded_files = f'{folder_path}/Loaded'
  processed_files = f'{folder_path}/Processed'




  return 

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

# To Do
def trading_csv_user_load():
    path_to_user_loaded_files = f'Data/{st.session_state.role_}/Trading/Loaded'
    archive_path = f'Data/{st.session_state.role_}/Trading/Archived'
    processed_files = f'Data/{st.session_state.role_}/Trading/Processed'

    if len(path_to_user_loaded_files) == 0 and 'final_output.csv' in processed_files:
      return
    elif len(path_to_user_loaded_files) == 0 and 'final_output.csv' not in processed_files:
      return st.write('No data was processed yet, please upload the data')
    else:
      df_main = pd.DataFrame()

      for index, file_name in enumerate(os.listdir(path_to_user_loaded_files)):
          if '.csv' in file_name:
              # Display the filtered dat
              df = pd.read_csv(path_to_user_loaded_files+f'/{file_name}')
              df_main = pd.concat([df_main,df])
              os.replace(path_to_user_loaded_files+f'/{file_name}', archive_path+f'/{file_name}')

      if len(df_main) > 0:
          df_main.sort_values(by='Date', ascending=True, inplace=True)
          if index > 0:
              df_main.drop_duplicates(inplace=True, subset=['Date','Desc','Amount','Ref'])
          df_main.reset_index(inplace=True, drop=True)

          if len(os.listdir(processed_files)) > 0:
              df = pd.read_csv(processed_files+f'/{os.listdir(processed_files)[0]}')
              df_main = pd.concat([df, df_main])
              df_main.sort_values(by='Date', ascending=True, inplace=True)
              df_main.drop_duplicates(inplace=True, subset=['Date','Desc','Amount','Ref'])
              df_main.reset_index(inplace=True, drop=True)

          df_main.to_csv(f'{processed_files}/final_output.csv', index=False)
          #loaded_date = datetime.today().strftime("%Y-%m-%d")
          
      df_main = pd.read_csv(f'{processed_files}/final_output.csv', )
      return #, loaded_date