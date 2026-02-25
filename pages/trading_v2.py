import streamlit as st
import utils.trading as trading
import utils.navigation as navigation
import pandas as pd
import sqlite3
from  utils import queries as qs
from datetime import datetime as dt
from pandas.tseries.offsets import DateOffset
import plotly.express as px

# Security 
if "role_" not in st.session_state:
    st.switch_page("app.py")

if 'data_stocks' not in st.session_state:
    data_stocks = pd.DataFrame({'Ticker':[],'Purchase Date':[],'Quantity':[],'Purchase Price':[]})
    st.session_state.data_stocks = data_stocks

if 'data_crypto' not in st.session_state:
    data_crypto = pd.DataFrame({'Ticker':[],'Purchase Date':[],'Quantity':[],'Purchase Price':[]})
    st.session_state.data_crypto = data_crypto

if 'data_bonds' not in st.session_state:
    data_bonds = pd.DataFrame({'Country':[],'Purchase Date':[],'Quantity':[],'Interest Rate':[],'Purchase Price':[],'Period':[]})
    st.session_state.data_bonds = data_bonds

if 'data_deposit' not in st.session_state:
    data_deposit = pd.DataFrame({'Bank':[],'Purchase Date':[],'Amount':[],'Interest Rate':[],'Period':[]})
    st.session_state.data_deposit = data_deposit

if "radio_sel" not in st.session_state:
    st.session_state.radio_sel = "Portfolio"

navigation.menu()

translations = {
    "title": {"ENG": "Finance Data", "POL": "Dane Finansowe"},
    "choose_file_": {"ENG": "If you have transaction detals in Excel please drop the file/s here", "POL": "Jezeli masz plik Excel z transakcjami, proszę załącz plik/i tutaj"},
    "type_mess": {"ENG": "we do not support other file types then csv or pdf", "POL": "aplikacja nie wspiera pliki innego typu niż xlsx"},
    "options": {"ENG": ['All Together','Bonds','Bank Deposit','Stocks','Crypto currencies'], "POL": ["Wszystko razem",'Obligacje','Lokata','Akcje','Krypto waluty']},
    "button1": {"ENG":"Submit", "POL":"Dodaj"},
    "data_":{'ENG':'Purch. Date (Y-m-d)', "POL":'Data Zakupu (Y-m-d)'},
    "volume_":{'ENG':'Amount', "POL":"Ilość"},
    "interest_rate_":{'ENG':'Interest rate','POL':'Stopy procentowe'},
    "purchase_price":{'ENG':'Purchase price', "POL":"Cena zakupu"},
    "length":{'ENG':'Type (in years)','POL':'Rodzja (w latach)'},
    "length2":{'ENG':'Type (in months)','POL':'Rodzja (w miesiącach)'},
    "error_mess1":{'ENG':'Please provide correct Ticker', "POL":"Podaj poprawny Ticker"},
    "error_mess2":{'ENG':'Please provide correct date format dd/mm/yyyy', "POL":"Podaj poprawny format daty dd/mm/yyyy"},
    "error_mess3":{'ENG':'Please provide volume', "POL":"Podaj ilość"},
    "error_mess4":{'ENG':'Please provide purchase price. If you do not know the price please leave it blank', "POL":"Podaj wartość zakupu. Jak nie znasz zostaw puste"},
    "genetal_error_message":{'ENG':'Something is wrong please restart the app','POL':'Ogólny błąd, proszę zrestartować aplikacje'}
    }

st.title(translations["title"][st.session_state.lang])

def add_dfForm_stocks():
    row = pd.DataFrame({'Ticker':[str.upper(st.session_state.ticker_stocks)],
                'Purchase Date':[st.session_state.p_date_stocks],
                'Quantity':[st.session_state.quant_stocks],
                "Purchase Price":[st.session_state.p_price_stocks]})
        
    st.session_state.data_stocks = pd.concat([st.session_state.data_stocks, row])

def add_dfForm_crypto():
    row = pd.DataFrame({'Ticker':[str.upper(st.session_state.ticker_crypto)],
                'Purchase Date':[st.session_state.p_date_crypto],
                'Quantity':[st.session_state.quant_crypto],
                "Purchase Price":[st.session_state.p_price_crypto]})
        
    st.session_state.data_crypto = pd.concat([st.session_state.data_crypto, row])

def add_dfForm_deposit():
    row = pd.DataFrame({
        'Bank':[str(st.session_state.bank_name)],
        'Purchase Date':[st.session_state.p_date_deposit],
        'Amount':[int(st.session_state.amount_deposit)],
        'Interest Rate':[float(st.session_state.interest_rate_deposit)],
        "Period":[int(st.session_state.period_deposit)]
        })
    
    st.session_state.data_deposit = pd.concat([st.session_state.data_deposit, row])
    st.session_state.data_deposit['Amount'] = st.session_state.data_deposit.groupby(['Bank','Purchase Date','Interest Rate','Period'])['Amount'].transform('sum')
    st.session_state.data_deposit.drop_duplicates(keep='first', inplace=True)
    st.session_state.data_deposit.reset_index(drop=True, inplace=True)

def add_dfForm_bonds(i):
    if sum(i) != 15:
        return
    row = pd.DataFrame({
        'Country':[str(st.session_state.country_bonds)],
        'Purchase Date':[st.session_state.p_date_bonds],
        'Quantity':[int(st.session_state.quant_bonds)],
        'Interest Rate':[float(st.session_state.interest_rate_bonds)],
        "Purchase Price":[int(st.session_state.p_price_bonds)],
        "Period":[int(st.session_state.length_bonds)]
        })
    
    st.session_state.data_bonds = pd.concat([st.session_state.data_bonds, row])
    st.session_state.data_bonds['Coupon_after_tax'] = st.session_state.data_bonds['Quantity'] * st.session_state.data_bonds['Purchase Price'] * st.session_state.data_bonds['Interest Rate'] * 0.81
    st.session_state.data_bonds['Quantity'] = st.session_state.data_bonds.groupby(['Country','Purchase Date','Interest Rate','Period'])['Quantity'].transform('sum')
    st.session_state.data_bonds['Coupon_after_tax'] = st.session_state.data_bonds.groupby(['Country','Purchase Date','Interest Rate'])['Coupon_after_tax'].transform('sum')
    st.session_state.data_bonds.drop_duplicates(keep='first', inplace=True)
    
    
#def save_to_db_bonds():   

_all_, _bonds_, _deposit_, _stocks_, _crypto_ = st.tabs(translations["options"][st.session_state.lang])

with _all_:
    st.write('all together')
with _bonds_:
    with st.form("form_bonds"):
        st.write("Please provide bonds transaction details")
        trade = []
        dfColumns1 = st.columns(3)
        dfColumns2 = st.columns(3)

        with dfColumns1[0]:
            st.text_input('Country', key='country_bonds')
        with dfColumns1[1]:
            st.text_input(translations["data_"][st.session_state.lang], key='p_date_bonds')
        with dfColumns1[2]:
            st.text_input(translations["volume_"][st.session_state.lang], key='quant_bonds')
        with dfColumns2[0]:
            st.text_input(translations["interest_rate_"][st.session_state.lang], key='interest_rate_bonds')
        with dfColumns2[1]:
            st.text_input(translations["purchase_price"][st.session_state.lang], key='p_price_bonds')
        with dfColumns2[2]:
            st.text_input(translations["length"][st.session_state.lang], key='length_bonds')
        i = []

        if len(st.session_state.country_bonds) != 0:
            i.append(1)
            trade.append(st.session_state.country_bonds)
                
        if len(st.session_state.p_date_bonds) == 10:
            i.append(2)
            trade.append(st.session_state.p_date_bonds)

        if len(st.session_state.quant_bonds) > 0:
            i.append(3)
            trade.append(st.session_state.quant_bonds)

        if len(st.session_state.interest_rate_bonds) != 0:
            i.append(4)
            trade.append(st.session_state.interest_rate_bonds)

        if len(st.session_state.p_price_bonds) >= 0:
            i.append(5)
            trade.append(st.session_state.p_price_bonds)

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit", on_click=add_dfForm_bonds(i), key='form_bonds')
        st.dataframe(st.session_state.data_bonds, hide_index=True)
        if submitted:
            if sum(i) == 15:
                pass
            elif sum(i) + 1 == 15:
                st.error(translations["error_mess1"][st.session_state.lang])
            elif sum(i) + 2 == 15:
                st.error(translations["error_mess2"][st.session_state.lang])
            elif sum(i) + 3 == 15:
                st.error(translations["error_mess3"][st.session_state.lang])
            elif sum(i) + 4 == 15:
                st.error('Please provide interest rate')
            else:
                st.error(translations["error_mess4"][st.session_state.lang])


    if len(st.session_state.data_bonds) > 0:
        st.write('implement pie-chart')
with _deposit_:
    
    with st.form("form_deposit"):
        st.write("Please provide bank deposit details")
        trade = []
        dfColumns = st.columns(5)
        with dfColumns[0]:
            st.text_input('Bank', key='bank_name')
        with dfColumns[1]:
            st.text_input(translations["data_"][st.session_state.lang], key='p_date_deposit')
        with dfColumns[2]:
            st.text_input(translations["volume_"][st.session_state.lang], key='amount_deposit')
        with dfColumns[3]:
            st.text_input(translations["interest_rate_"][st.session_state.lang], key='interest_rate_deposit')
        with dfColumns[4]:
            st.text_input(translations["length2"][st.session_state.lang], key='period_deposit')

        i = []

        if len(st.session_state.bank_name) != 0:
            i.append(1)
            trade.append(st.session_state.bank_name)
                
        if len(st.session_state.p_date_deposit) == 10:
            i.append(2)
            trade.append(st.session_state.p_date_deposit)

        if len(st.session_state.amount_deposit) > 0:
            i.append(3)
            trade.append(st.session_state.amount_deposit)

        if len(st.session_state.interest_rate_deposit) != 0:
            i.append(4)
            trade.append(st.session_state.interest_rate_deposit)

        if len(st.session_state.period_deposit) > 0:
            i.append(5)
            trade.append(st.session_state.period_deposit)

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit", on_click=add_dfForm_deposit, key='form_deposit')
        if len(st.session_state.data_deposit) > 0:
            st.dataframe(st.session_state.data_deposit, hide_index=True)
        if submitted:

            if sum(i) == 15:
                pass
            elif sum(i) + 1 == 15:
                st.error(translations["error_mess1"][st.session_state.lang])
            elif sum(i) + 2 == 15:
                st.error(translations["error_mess2"][st.session_state.lang])
            elif sum(i) + 3 == 15:
                st.error(translations["error_mess3"][st.session_state.lang])
            elif sum(i) + 4 == 15:
                st.error('Please provide interest rate')
            else:
                st.error(translations["error_mess4"][st.session_state.lang])
        analysis_ = False
        if len(st.session_state.data_deposit) > 0 or sum(i)==15:
            button_columns = st.columns(2)
            with button_columns[0]:
                submit_to_db = st.form_submit_button("Save to DB")
                if submit_to_db:
                    qs.post_user_deposit(st.session_state.role_, st.session_state.data_deposit)
            with button_columns[1]:
                analysis_ = st.form_submit_button('Show analysis')

    if analysis_ == True:
        single, combined = st.tabs(['Single','Combined'])
        df_deposit_all = pd.DataFrame()
        for deposit in range(0,len(st.session_state.data_deposit)):
            period = int(st.session_state.data_deposit.iloc[deposit, -1])
            inv_value = int(st.session_state.data_deposit.iloc[deposit, 2])
            df_deposit = pd.DataFrame()

            for month_ in range(0,period):
                row = pd.DataFrame({'Bank':[1], 'Purchase Date':[2], 'Amount':[3], 'Interest Rate':[4], 'Period':[5], 'Coupon':[6]})
                row['Bank'] = st.session_state.data_deposit.iloc[deposit,0]
                row['Purchase Date'] = pd.to_datetime(st.session_state.data_deposit.iloc[deposit,1]) +  DateOffset(months=month_)
                
                if month_ == 0:
                    row['Amount']= round((st.session_state.data_deposit.iloc[deposit,2] * st.session_state.data_deposit.iloc[deposit,3]) /12 + st.session_state.data_deposit.iloc[deposit,2],2)
                else:
                    row['Amount'] = round((st.session_state.data_deposit.iloc[deposit,2] * st.session_state.data_deposit.iloc[deposit,3]) /12 + float(df_deposit.iloc[month_-1,2]),2)
                
                row['Interest Rate']= st.session_state.data_deposit.iloc[deposit,3]
                row['Period']= month_ + 1
                row['Coupon'] = row['Amount'] - inv_value
                df_deposit = pd.concat([df_deposit, row])

            df_deposit_all = pd.concat([df_deposit_all, df_deposit])

        with combined:
            st.write('in progress')
            df_deposit_all_combined = df_deposit_all.copy()
            df_deposit_all_combined['Year-Month'] = df_deposit_all_combined['Purchase Date'].dt.strftime('%Y-%m')
            df_dep_com_groupby_sum = df_deposit_all_combined.groupby('Year-Month').sum()
            df_dep_com_groupby_avg = df_deposit_all_combined.groupby('Year-Month').mean()
            st.line_chart(df_dep_com_groupby_sum, y='Amount')
            st.line_chart(df_dep_com_groupby_avg, y='Interest Rate')
        with single:
            df_deposit_all['Purchase Date'] = df_deposit_all['Purchase Date'].dt.strftime('%Y-%m-%d')
            df_pie_chart = df_deposit_all.groupby(['Bank']).max('Coupon')
            st.title('Detailed view')
            st.dataframe(df_deposit_all, hide_index=True)
            st.title('Over Time')
            st.line_chart(df_deposit_all, x="Purchase Date", y="Coupon" , color ='Bank')
            st.title('Distribution of Deposits')
            fig = px.pie(df_pie_chart, values='Amount', names=df_pie_chart.index)
            st.plotly_chart(fig, use_container_width=True)

    if len(qs.get_user_deposit(st.session_state.role_))>0:
        st.write('There should be something')
        st.dataframe(qs.get_user_deposit(st.session_state.role_))



with _stocks_:
    uploaded_files = st.file_uploader(
    translations["choose_file_"][st.session_state.lang], accept_multiple_files=True, key='stocks')

    for uploaded_file in uploaded_files:
        suffix = uploaded_file.name.split('.')[-1]
        if suffix == 'xlsx':
            trading.streamlit_uploaded_file_trading(uploaded_file)
        else:
            st.write(translations["type_mess"][st.session_state.lang])


    with st.form("form_stocks"):
        st.write("Please provide stocks transaction details")
        trade = []
        dfColumns = st.columns(4)
        with dfColumns[0]:
            st.text_input('Ticker', key='ticker_stocks')
        with dfColumns[1]:
            st.text_input(translations["data_"][st.session_state.lang], key='p_date_stocks')
        with dfColumns[2]:
            st.text_input(translations["volume_"][st.session_state.lang], key='quant_stocks')
        with dfColumns[3]:
            st.text_input(translations["purchase_price"][st.session_state.lang], key='p_price_stocks')
        i = []

        if len(st.session_state.ticker_stocks) != 0 and len(st.session_state.ticker_stocks) < 10:
            i.append(1)
            trade.append(st.session_state.ticker_stocks)
                
        if len(st.session_state.p_date_stocks) == 10:
            i.append(2)
            trade.append(st.session_state.p_date_stocks)

        if len(st.session_state.quant_stocks) > 0:
            i.append(3)
            trade.append(st.session_state.quant_stocks)

        if len(st.session_state.p_price_stocks) >= 0:
            i.append(4)
            trade.append(st.session_state.p_price_stocks)

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit", on_click=add_dfForm_stocks, key='form_stocks')
        if submitted:
            if sum(i) == 10:
                st.dataframe(st.session_state.data_stocks)
            elif sum(i) + 1 == 10:
                st.error(translations["error_mess1"][st.session_state.lang])
            elif sum(i) + 2 == 10:
                st.error(translations["error_mess2"][st.session_state.lang])
            elif sum(i) + 3 == 10:
                st.error(translations["error_mess3"][st.session_state.lang])
            else:
                st.error(translations["error_mess4"][st.session_state.lang])

    
    # show already exsisting stocks:            
    

with _crypto_:
    uploaded_files = st.file_uploader(
    translations["choose_file_"][st.session_state.lang], accept_multiple_files=True, key='crypto')

    for uploaded_file in uploaded_files:
        suffix = uploaded_file.name.split('.')[-1]
        if suffix == 'xlsx':
            trading.streamlit_uploaded_file_trading(uploaded_file)
        else:
            st.write(translations["type_mess"][st.session_state.lang])

    with st.form("form_crypto"):
        st.write("Please provide crypto transaction details")
        trade = []
        dfColumns = st.columns(4)
        with dfColumns[0]:
            st.text_input('Ticker', key='ticker_crypto')
        with dfColumns[1]:
            st.text_input(translations["data_"][st.session_state.lang], key='p_date_crypto')
        with dfColumns[2]:
            st.text_input(translations["volume_"][st.session_state.lang], key='quant_crypto')
        with dfColumns[3]:
            st.text_input(translations["purchase_price"][st.session_state.lang], key='p_price_crypto')
        i = []

        if len(st.session_state.ticker_crypto) != 0 and len(st.session_state.ticker_crypto) < 10:
            i.append(1)
            trade.append(st.session_state.ticker_crypto)
                
        if len(st.session_state.p_date_crypto) == 10:
            i.append(2)
            trade.append(st.session_state.p_date_crypto)

        if len(st.session_state.quant_crypto) > 0:
            i.append(3)
            trade.append(st.session_state.quant_crypto)

        if len(st.session_state.p_price_crypto) >= 0:
            i.append(4)
            trade.append(st.session_state.p_price_crypto)

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit", on_click=add_dfForm_crypto, key='form_crypto')
        if submitted:
            if sum(i) == 10:
                st.dataframe(st.session_state.data_crypto)
            elif sum(i) + 1 == 10:
                st.error(translations["error_mess1"][st.session_state.lang])
            elif sum(i) + 2 == 10:
                st.error(translations["error_mess2"][st.session_state.lang])
            elif sum(i) + 3 == 10:
                st.error(translations["error_mess3"][st.session_state.lang])
            else:
                st.error(translations["error_mess4"][st.session_state.lang])