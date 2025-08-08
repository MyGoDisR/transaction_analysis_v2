import pandas as pd
import numpy as np
from pypdf import PdfReader
from os import listdir
import os
import streamlit as st

import fitz
import pathlib
import re

#### PDF data to tabular form ###########################################################################################################################################

def data_to_df():
  folder_path = f'Data/{st.session_state.role_}'
  path_to_user_loaded_files = f'Data/{st.session_state.role_}/Loaded'
  archive_path = f'Data/{st.session_state.role_}/Archived'
  processed_files = f'Data/{st.session_state.role_}/Processed'

  if "Archived" not in listdir(folder_path):
        os.makedirs(folder_path+"/Archived")

  if len(path_to_user_loaded_files) == 0 and 'final_output.csv' in processed_files:
      return pd.read_csv(f'{processed_files}/final_output.csv')

  df_pko = pd.DataFrame() #PKO trans
  df_main = pd.DataFrame() # BNP transactions
  df_bnp = pd.DataFrame() # BNP transactions
  df_bnp_2 = pd.DataFrame() # BNP transactions from app
  df_sant = pd.DataFrame() #Santander transactions

  for index, file_ in enumerate(listdir(path_to_user_loaded_files)):
    st.write(file_)
    # PKOBP
    if 'Wyciag_' in file_: 
      pdfbytes = pathlib.Path(path_to_user_loaded_files+'/'+file_).read_bytes()
      # from here on, file oldname.pdf is fully available
      doc = fitz.open("pdf", pdfbytes)
      pattern = re.compile(r'[0-3][0-9].[0-1][0-9].[2][0][0-9][0-9]')
      context = []

      for index_page, page in enumerate(doc):
        if index_page < int(len(doc)-1):
          text = page.get_text()
          page_content = text.split('\n')[text.split('\n').index('Opis operacji')+1:text.split('\n').index('Saldo do przeniesienia')]

          dates_ = []
          for index,i in enumerate(page_content):
            if index < len(page_content)-1:
              if pattern.match(i) and len(i)==10 and len(page_content[index+1]) == 17 :
                dates_.append(index)
            else:
              if pattern.match(i) and len(i)==10:
                dates_.append(index)

          j = 0
          for i in dates_[1:]:
            context.append(page_content[j:i])
            j = i

        else:
          text = page.get_text()
          page_content = text.split('\n')[text.split('\n').index('Opis operacji')+1:text.split('\n').index('Saldo końcowe')]

          dates_ = []
          for index,i in enumerate(page_content):
            if index < len(page_content)-1:
              if pattern.match(i) and len(i)==10 and len(page_content[index+1]) == 17 :
                dates_.append(index)
            else:
              if pattern.match(i) and len(i)==10:
                dates_.append(index)
          j = 0
          for i in dates_[1:]:
            context.append(page_content[j:i])
            j = i
        df_pko = pd.concat([df_pko, pd.DataFrame(context)])
      
    elif 'Account statement number' in file_:
      pdfbytes = pathlib.Path(path_to_user_loaded_files+'/'+file_).read_bytes()
      # this way the file is not open and can be moved
      doc = fitz.open("pdf", pdfbytes)
      patter = re.compile(r'[0-9][0-9].[0-1][0-9].[2][0][2-5][0-9]')
      context = []

      for index_page, page in enumerate(doc):
        text = page.get_text()
        # list to append single transactions
        occ = []

        if index_page < len(doc):
          beg_phrase = 'po operacji'
          end_phrase = 'BNP Paribas Bank Polska Spółka Akcyjna z siedzibą w Warszawie przy ul. Kasprzaka 2, 01-211 Warszawa, zarejestrowany w rejestrze przedsiębiorców Krajowego Rejestru Sądowego'
          if 'po operacji' in text.split('\n'): #sometimes the fitz library does not read the first line in which 'po operacji lies therefore it will start from the first row
            page_content = text.split('\n')[text.split('\n').index(beg_phrase)+1:text.split('\n').index(end_phrase)]
          else:
            page_content = text.split('\n')[0:text.split('\n').index(end_phrase)]
        else:
          beg_phrase = 'po operacji'
          end_phrase = 'Niniejszy wyciąg bankowy jest zestawieniem wszystkich operacji dokonanych na rachunku bankowym wygenerowanym elektronicznie na podstawie art. 7 ustawy Prawo Bankowe (Dz.U. Nr 140 z 1997 roku, poz.'
          page_content = text.split('\n')[text.split('\n').index(end_phrase)-12:text.split('\n').index(end_phrase)]
          overall_info = text.split('\n')[text.split('\n').index(end_phrase)-12:text.split('\n').index(end_phrase)]

        for index,line in enumerate(page_content):
          if patter.match(line):
            occ.append(index)

        for i in range(0,len(occ),2):
          df_bnp_2 = pd.concat([df_bnp_2, pd.DataFrame(page_content[occ[i]:occ[i]+10]).T])

    elif 'WYCIAG_BANKOWY_' in file_:
      for nr_page in range(0,(len(PdfReader(path_to_user_loaded_files+'/'+file_).pages))):
        page_content = PdfReader(path_to_user_loaded_files+'/'+file_).pages[nr_page].extract_text()
        if nr_page == 0:
          beg_phrase = page_content.index('SALDO POCZĄTKOWE')
          end_phrase = page_content.index('BNP Paribas Bank Polska Spółka Akcyjna z siedzibą w Warszawie ')
        elif nr_page == len(PdfReader(path_to_user_loaded_files+'/'+file_).pages)-1:
          if 'Saldo po operacji' not in page_content:
            continue
          else:
            beg_phrase = page_content.index('Saldo po operacji')
            end_phrase = page_content.index('Niniejszy wyciąg bankowy jest zestawieniem wszystkich operacji dokonanych na rachunku bankowym')
        else:
          beg_phrase = page_content.index('Saldo po operacji')
          end_phrase = page_content.index('BNP Paribas Bank Polska Spółka Akcyjna z siedzibą w Warszawie ')
          
        a = page_content[beg_phrase:end_phrase].split('\n')
        
        occurencies = []
        patter = re.compile(r'[A-Z][A-Z][A-Z][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]')

        for index,line in enumerate(a):
          if patter.match(line):
            occurencies.append(index)

        for index,i in enumerate(occurencies):
          if index == 0:
            if 'Data waluty' in a[i+1]:
              end_point = i+3
              one_item = a[1:end_point-2]+ [a[end_point-1]]
              if len(one_item) <= 8:
                df_main = pd.concat([df_main, pd.DataFrame(one_item).T])
              else:
                df_main = pd.concat([df_main, pd.DataFrame(one_item[:3] + one_item[4:]).T])
              last_point = end_point
            
            elif 'BLIK' in a[2]:
              end_point = i+2
              one_item = a[1:3] + a[6:end_point]

              if len(one_item) <= 8:
                df_main = pd.concat([df_main, pd.DataFrame(one_item).T])
              else:
                df_main = pd.concat([df_main, pd.DataFrame(one_item[:3] + one_item[4:]).T])
              last_point = end_point

            else:
              end_point = i+2
              one_item = a[1:end_point]
                    
              if len(one_item) <= 8:
                df_main = pd.concat([df_main, pd.DataFrame(one_item).T])
              else:
                df_main = pd.concat([df_main, pd.DataFrame(one_item[:3] + one_item[4:]).T])
              last_point = end_point
          # not first page
          else:
            if 'Rachunek oszczędnościowo-rozliczeniowy' in a[last_point]:
              last_point = last_point + 7

            if 'Data waluty' in a[i+1]:
              end_point = i+3
              df_main = pd.concat([df_main, pd.DataFrame(a[last_point:end_point-2]+ [a[end_point-1]]).T])
              last_point = end_point
            elif 'BLIK' in a[last_point+1]:
              end_point = i+2
              one_item = a[last_point:last_point+2] + a[last_point+6:end_point]
              if len(one_item) <= 8:
                df_main = pd.concat([df_main, pd.DataFrame(one_item).T])
              else:
                df_main = pd.concat([df_main, pd.DataFrame(one_item[:3] + one_item[4:]).T])
              last_point = end_point
            elif 'OPŁATA ZA RACHUNEK/PAKIET' in a[last_point+1]:
              end_point = i+2
              df_main = pd.concat([df_main, pd.DataFrame(a[last_point:last_point+3] + ['0','0','0','0'] + [a[last_point+3]]).T])
              one_item = a[last_point+4:end_point]
              if len(one_item) <= 8:
                df_main = pd.concat([df_main, pd.DataFrame(one_item).T])
              else:
                df_main = pd.concat([df_main, pd.DataFrame(one_item[:3] + one_item[4:]).T])
              last_point = end_point
            else:
              end_point = i+2
              one_item = a[last_point:end_point]
              if len(one_item) <= 8:
                df_main = pd.concat([df_main, pd.DataFrame(one_item).T])
              else:
                df_main = pd.concat([df_main, pd.DataFrame(one_item[:3] + one_item[4:]).T])
              last_point = end_point
          df_bnp =  pd.concat([df_bnp, df_main])
      
    elif 'Santander' in file_:
      for i in range(0,len(PdfReader(path_to_user_loaded_files+'/'+file_).pages)):
        # naming convention less explanatory more space convinient
        a = PdfReader(path_to_user_loaded_files+'/'+file_).pages[i].extract_text().split('\n')

        occur = []
        patter = re.compile(r'[0-3][0-9] [a-z][a-z][a-z] [2][0][1-5][0-9]')

        # finding the patter to find where one transactions starts/ends
        for index, line in enumerate(a):
          if patter.match(line):
            occur.append(index)

        for ind,i in enumerate(occur[:-1]):
          if len(a[i:occur[ind+1]]) == 3:
            df_sant = pd.concat([df_sant,pd.DataFrame([a[i]] + [a[occur[ind+1]-3]] + a[occur[ind+1]-1].replace(',','.').replace(' ','').split('PLN')[:-1] + [re.search(r'[-+]?\d+\.\d{2}(?!\d)', a[occur[ind+1]-1].replace(',','.').replace(' ','').split('PLN')[0]).group()]).T])
          else:
            df_sant = pd.concat([df_sant,pd.DataFrame([a[i]] + [a[occur[ind+1]-4]] + [a[occur[ind+1]-3]+' '+a[occur[ind+1]-2]] + [a[occur[ind+1]-1].replace(',','.').replace(' ','').split('PLN')[-2]] + [a[occur[ind+1]-1].replace(',','.').replace(' ','').split('PLN')[-3]]).T])
        # last occurence in the page
        if len(a[occur[-1]:-1]) == 3:
          df_sant = pd.concat([df_sant,pd.DataFrame([a[occur[-1]]]  + [a[occur[ind+1]+1]] +a [-2].replace(',','.').replace(' ','').split('PLN')[:-1] + ['0']).T])
        else:
          df_sant = pd.concat([df_sant, pd.DataFrame([a[occur[-1]]] + [a[occur[ind+1]+1]] + [a[-3]] + [a[-2].replace(',','.').replace(' ','').split('PLN')[-2]] + [a[-2].replace(',','.').replace(' ','').split('PLN')[-3]]).T])
    os.replace(path_to_user_loaded_files+f'/{file_}', archive_path+f'/{file_}')


  if len(df_pko.columns) == 9:
    df_pko = df_pko.set_axis(['Date','Ref','Trans. type','Amount','Run_balance','Date_2','In-depth Desc.','In-depth Desc._2','In-depth Desc._3'], axis=1)
  elif len(df_pko.columns) == 10:
     df_pko = df_pko.set_axis(['Date','Ref','Trans. type','Amount','Run_balance','Date_2','In-depth Desc.','In-depth Desc._2','In-depth Desc._3','del'], axis=1)

  # Assigning Tags to transactions
  # list of shops
  food_shops = ['biedronka','auchan','lidl','kaufland','carrefour','aldi','sklep spozywczy','zabka','STOKROTKA','BAJPIX','DELIKATES','TSS','NETTO','PIEKARNIA',
                'CUKIERNIA','ART. SPOZ','KIOSK','Supermarket','1minute','SMAK','Firma Handlowa','INTERMARCHE','Tchibo','LITTLE INDIA','Duty','Zator','WODNIK',
                'KrakPres','AWITEKS','JMT','ADM24','UL. ELEKTRYCZNA 2/U5','UL. SZEWSKA 27','Kaszubskie','UL. KASZUBSKA','UL. SIKORKI 21A','Al.capone','RUCH',
                'TESCO','DINO','FRESHMARKET','CARERREFOUR EXPRESS','Swiat Alkoholi','MALE MOLO SOPOT','Warszawska Bagieta','EUROSPAR','POLOMARKET','Hale Banacha',
                'Alkohole 24','PIOTR I PAWEL','Piotr i Pawel','Relay','OWOCE WARZYWA','1-Minute','Rolmies','ZIARNA ZYCIA WARSZAWA','Virgin','KERANISS SP. Z O.O. BALICE',
                'FH "Eldomek" Tarnow','AUTOMAT M21 KRAKOW','GRAWITON','SWIEZACZEK','HALIMA ENTERPRISE3282Tarnow','DANIEL BNP', 'BIEDRONKA']

  outting = ['Gospoda','McDonalds','KRYTA PLYWALNIA','Strusinianka','Goracy Precel','LOCKEDUP.PL','JUST MEAT','KLUB BILARDOWY','PIZZERIA','KEBAB','RESTAURACJA',
            'PIZZA','BISTRO','frytki','SILVER DRAGON','COFFEE','NOWY KRAFTOWY','BAR','SZKLANKI','MEAT HOUSE','BOH','FITNESS',
            'NEGRONI','lockme','Los Gorditos','Hawaiian Bowls','POL NA POL','GRUBA BULA','HAMSA','Park Zdrojowy','EXITROO','Gora','energylandia', 'pyszne',
            'ebilet','wyjatkowyprezent','superprezenty','KAJAKWSTOLICY','multikino', 'kopalnia','cinema', 'MEET& EAT','www.tck.pl','kfcdostawa','ZDROWY PROJEKT',
            'Lubicz/Pawia/Basztowa/Wes Kraków','Burger King','American Dream','KAWIARNIA','CAFE','SLODKA','CHILLI MILI','Piwiarnia WARKA', 'Kawa',
            'CZARNY SEZAM','TBILISURI','RAMENPOL','AKWARIUM','HALA CENTRALNA','BOM DIA FABRICA DE PAST','TENDUR KEBAP&GRILL','PHUONG THAO','KFC','Wolt',
            'SLIWKA W KOMPOT','MOA Burger Krakow','MUZEUM','PUTKA','SPEC','Mr. Pancake','UNDER SEOUL','LODZIARNIE','GDYNSKA RYBKA','BREAK AND LUNCH',
            'KINO','Starbucks','CRAZY BUBBLE','KUCHNIE SWIATA','BYDLO I POWIDLO','MIEJSKI OGROD','WARSHISHAWA','GRUZIN NA','ROWAR MIEJSKI SOPOT','KLUB BILLBOARD',
            'ALE BURGER','ZAGRYWKI WARSZAWA','CENTRUM NAUKI','GREEN CAFFE NERO','LA NONNA','PILI PALILI','ESSO LAMPERTI COMO','Serwis Gastronomiczn','DELIFISH GDANSK',
            'LA BELLA Katarzy Tarnow','SASSY CLUB AND','SRODMIESCIE Gdynia','IRISH PUB LEPRIKON','FETTA DI ITALIA','BOMBAJ MASALA','HIMALAYA NEPAL','POKOJ NA LATO',
            'Gdynia Riviera','GEMINI TARNOW','Galeria MokotowWarszawa','USLUGI GASTRONOMICZNEKAMIENIEC','TANDYR HOUSE','FOODIX','FARAON RAMY FAROUKTARNOW','SQ KOLMEX Warszawa',
            'ANTRESOLA','BROWAR TARNOWSKI','MARSZALKOWSKA 140 R','TOP RESTAURACJE_MODEL','BULKA Sp. z o.o. Warszawa','MAMUSZKI 14 SOPOT PL','WEJHEROWSKIE CENTRUM KWEJHEROWO',
            'SK BROTHERS RAJIB AL MTARNOW','PUEBLOGDANSK','NOOR FALCON','BK KRAKOW DWORZEC GLOWKRAKOW','ANDIAMO GROUP Dom53767Gdynia PL','AGATA WOZNIAK FRESHKRAKOW',
            'Zupnik Wieliczka','RAMEN SUSHI','ANDIAMO GROUP Dom53767Gdynia', 'NIKACONOPIA SOPOT','NEW VEGAS Warszawa', 'AURA WARSZAWA PL','GASTER Warszawa PL',
            'PHO 206 WARSZAWA','PL PH KRAKOW M1','GASTRONMECHELINKI','Obozna 11','147 BREAK Warszawa PL','ARANEUS WALBRZYCH','OTTOMANSKA POKUSAWARSZAWA','Z.G.H W.WALLONI TARNOW']

  clothing_shops = ['SORTEX','www.zalando.d','Nike','HALF PRICE','DECATHLON','TK Maxx','PULL & BEAR','MARTES','allegro','SINSAY','sportano','eobuwie',
                    'EUROBUT','CROPP','BONARKA','mebags','wearmedicine','DABROWSKIEGO 25/1 TARNOW','ANTISOCIAL','RESERVED','HM', 'MEDICINE',
                    'VAN GRAAF','TANIE UBRANIE','DHL PARCEL','SZMIZJERKA','CCC','PRALNIA DELFIN TARNOW','TERA WARSZAWA PL','DPD POLSKA','KIK TEXTIL']

  necessity = ['doladowania','NETFLIX','ebok.vectra.pl','KUZNIA JEWULA','SPOTIFY','APTEKA','Legimi','FOTO','SALON','Ewelina Dulak','siepomaga','rankomat','DOŁADOWANIE TELEFONU','amazon',
              'zrzutka.pl','upc', 'wosp','mydr','UL. SW. SEBASTIANA 11 KRAKOW','PlayStation Network','BookBit','Disney Plus','HBO MAX','Super - Pharm','CEFARM-WARSZAWA']

  home_shops = ['action','pepco','teddy','obi','castorama','leroy merlin','x-kom','EMPIK','homla','EURO NET','JYSK','FORPEPE','floribunda','ATUT','morele','aliexpress','mediaexpert',
                'steampowered','tadar.pl','www.bnpparibas.pl','KOMPUTORNIK','KWIACIARNIA BADYLEK','MEDIA MARKT','TEDI','HOME AND YOU','DEALZ','W.GRAJEK-KWIATY','BALTA WEJHEROWO',
                'Xerografia','TIGER WARSZAWA','TOMASZ DYCHTON TARNOW','GSM ZONE ADRIAN KOWALTARNOW', 'FORMATKA','PHU StaCom Krzysztof Kl TarnowPL','CRAZY GSM S.C. WEJHEROWO']

  beauty_shops = ['rossman','hebe','douglas','sephora','KONTIGO','NATURA','lilou','flaconi','notino','piercingxxl','KUZNIA FRYZJERSKA','Jewelry','Pandora','Pracownia Artysty',
                  'ATELIER FRYZJERSK1784','GALERIA USMIECHU']

  commute = ['przewozy regionalne','astariu','mpk','ztm','unicard','koleo','intercity','BILETOMAT','KOLEJE','BILETY','bilkom','mka','PKP','Parking', 
            'BLIK - bilet na przejazd','veturilo','ORLEN','napieknewlosy','imoje.pl','CIRCLE K','SHELL','BOLT','UBER','AUT BILET',
            'FREENOW','STACJA PALIW','PANEK CAR','BATEX -VENDING WARSZAWA','BILETOM','AUTO-SZYBY','STACJA OBSLUGI SAMOCHOWARSZAWA',
            'MPSA - A 208 WARSZAWA P','OSP W KOSAKOWIE','KTD SP. Z O.O.', 'AUTOMATY MM CONCEPTPIASTOW', 'MPSA - A 84 WARSZAWA','SSPP GDYNIA','WARSZAWA ASEC SAWARSZAWA',
            'SPP WARSZAWA 2 WARSZAWAPL']
  
  travel = ['HOTEL','TRIP','Ministry of Home Affai New','LS AIRPORT SERVICES','Hotel NIKIFOR','lot','AIRBNB','kapsulahostel','e-podroznik','wiemgdziejade','WIZZ','live.adyen.com']

  hobby = ['squashtarnow','pilkanahali','maraton','sts-timing','AVATAR','CUBE WALLS','ncyklopediakryptowalut','roadmapaprogramisty','betclic','dostartu','zis','groupon','mybenefit',
          'UL. KLIMECKIEGO 14 KRAKOW','BookBeat PL','MOOD','CITYFIT','ROJAX','TACJA NARCIARSKA7471Siemiechow','PROFI BIKE ROWERY KROSSWARSZAWA','TheBooks.pl','KDJ Forma','BP-REDUTA JET WASH',
          'MONDLY','SKLEP BIEGACZA']
  
  salary = ['wyplata','wynagrodzenie','za umowe','Wynagrodzenie']

  saveings = ['SAVINGS']

  rent = ['SIKORKI', 'RENT-', 'ZA MIESIAC', 'ZA LIPIEC']

  # Create a regex pattern from the list of words
  pattern_food = '|'.join(food_shops)
  pattern_home = '|'.join(home_shops)
  pattern_beauty = '|'.join(beauty_shops)
  pattern_commute = '|'.join(commute)
  pattern_clothing = '|'.join(clothing_shops)
  pattern_outting = '|'.join(outting)
  pattern_necessity = '|'.join(necessity)
  pattern_hobby = '|'.join(hobby)
  pattern_salary = '|'.join(salary)
  pattern_rent = '|'.join(rent)
  pattern_savings = '|'.join(saveings)
  pattern_travel = '|'.join(travel)


  if len(df_pko) != 0:
    df_pko['Desc'] = df_pko['In-depth Desc.'].astype(str) + df_pko['In-depth Desc._2'].astype(str) + df_pko['In-depth Desc._3'].astype(str)
    df_pko = df_pko.loc[:,('Date','Ref','Trans. type','Amount','Run_balance','Desc')]

    df_pko.drop_duplicates(inplace=True)

    df_pko['Date'] = pd.to_datetime(df_pko['Date'])
    df_pko['Trans. type'] = df_pko['Trans. type'].astype(str)
    df_pko['Run_balance'] = df_pko['Run_balance'].str.replace(" ","",regex=True).replace(',','.', regex=True).astype(float)
    df_pko['Amount'] = df_pko['Amount'].str.replace(" ","",regex=True).replace(',','.',regex=True).astype(float)
    df_pko['C/D'] = np.where(df_pko['Amount'] > 0, 'D', 'C')
    df_pko['Amount'] = df_pko['Amount'].astype(str).str.replace("-","",regex=True).astype(float)
    df_pko['Desc'] = df_pko['Desc'].astype(str)
    df_pko['Type'] = 'Others'  

    df_pko = df_pko.sort_values('Date')
        
    # Wrangling descriptions
    df_pko.loc[df_pko['Trans. type'].str.contains("WYMIANA W KANTORZE", case=False, na=False), 'Type'] = "FX_exchange"
    df_pko.loc[df_pko['Trans. type'].str.contains("PRZELEW PRZYCH. SYSTEMAT. WPŁYW", case=False, na=False), 'Type'] = "Inflow"
    df_pko.loc[df_pko['Trans. type'].str.contains("PRZELEW PRZYCHODZĄCY", case=False, na=False), 'Type'] = "Inflow"
    df_pko.loc[df_pko['Trans. type'].str.contains("WPŁATA GOTÓWKI WE WPŁATOMACIE", case=False, na=False), 'Type'] = "Inflow"
    df_pko.loc[df_pko['Trans. type'].str.contains("PRZELEW NATYCHMIASTOWY", case=False, na=False), 'Type'] = "Inflow"
    df_pko.loc[df_pko['Trans. type'].str.contains("PRZELEW WYCHODZĄCY", case=False, na=False), 'Type'] = "Outflow"
    df_pko.loc[df_pko['Trans. type'].str.contains("PRZELEW NA TELEFON WYCHODZĄCY ", case=False, na=False), 'Type'] = "Outflow"
    df_pko.loc[df_pko['Trans. type'].str.contains("PRZELEW NA TELEFON PRZYCHODZ", case=False, na=False), 'Type'] = "Inflow"
    #df_pko.loc[df_pko['Trans. type'].str.contains("PRZELEW ZAKUP BILETU", case=False, na=False), 'Type'] = "Commute"
    #df_pko.loc[df_pko['Trans. type'].str.contains("ZAKUP PRZY UŻYCIU KARTY", case=False, na=False), 'Type'] = "Outflow"
    df_pko.loc[df_pko['Trans. type'].str.contains("WYPŁATA W BANKOMACIE", case=False, na=False), 'Type'] = "Outflow"
    df_pko.loc[df_pko['Trans. type'].str.contains("WYPŁATA", case=False, na=False), 'Type'] = "Outflow"
    df_pko.loc[df_pko['Trans. type'].str.contains("WPŁATA", case=False, na=False), 'Type'] = "Inflow"
    df_pko.loc[df_pko['Trans. type'].str.contains("OPŁATA - PRZELEW NATYCH. WYCH.", case=False, na=False), 'Type'] = "Outflow"
    df_pko.loc[df_pko['Trans. type'].str.contains("KAPIT.ODSETEK KARNYCH-OBCIĄŻENIE", case=False, na=False), 'Type'] = "Outflow"

    df_pko.loc[df_pko['Desc'].str.contains(pattern_food, case=False, na=False), 'Type'] = 'Food'
    df_pko.loc[df_pko['Desc'].str.contains(pattern_home, case=False, na=False), 'Type'] = 'House appliencies'
    df_pko.loc[df_pko['Desc'].str.contains(pattern_beauty, case=False, na=False), 'Type'] = 'Beauty'
    df_pko.loc[df_pko['Desc'].str.contains(pattern_commute, case=False, na=False), 'Type'] = 'Commute'
    df_pko.loc[df_pko['Desc'].str.contains(pattern_clothing, case=False, na=False), 'Type'] = 'Clothing'
    df_pko.loc[df_pko['Desc'].str.contains(pattern_outting, case=False, na=False), 'Type'] = 'Outting'
    df_pko.loc[df_pko['Desc'].str.contains(pattern_necessity, case=False, na=False), 'Type'] = 'Necessities'
    df_pko.loc[df_pko['Desc'].str.contains(pattern_hobby, case=False, na=False), 'Type'] = 'Hobby'
    df_pko.loc[df_pko['Desc'].str.contains(pattern_salary, case=False, na=False), 'Type'] = 'Salary'
    df_pko.loc[df_pko['Desc'].str.contains(pattern_rent, case=False, na=False), 'Type'] = 'Rent'
    df_pko.loc[df_pko['Desc'].str.contains(pattern_savings, case=False, na=False), 'Type'] = 'Savings'
    df_pko.loc[df_pko['Desc'].str.contains(pattern_travel, case=False, na=False), 'Type'] = 'Travel'
  
  if len(df_bnp_2) != 0:
    # description column
    df_bnp_2[10] = df_bnp_2[7] + ' ' + df_bnp_2[8] + ' ' + df_bnp_2[9]
    # unnecessary columns
    df_bnp_2 = df_bnp_2.iloc[:,[1,2,3,4,10]]
    df_bnp_2[1] = pd.to_datetime(df_bnp_2[1], format ="%d.%m.%Y")
    df_bnp_2 = df_bnp_2.sort_values(by=1)
    df_bnp_2.reset_index(drop=True, inplace=True)
    df_bnp_2.rename(columns={1:'Date',2:'Amount',3:'Run_balance',4:'Type',10:'Desc'}, inplace=True)
    df_bnp_2['Amount'] = df_bnp_2['Amount'].str.replace(',','.').str.replace('\xa0','').astype(float)
    df_bnp_2['Run_balance'] = df_bnp_2['Run_balance'].str.replace('-','').str.replace(',','.').str.replace('\xa0','').astype(float)
    # Credit / Debit
    df_bnp_2['C/D'] = np.where(df_bnp_2['Amount'] > 0, 'D', 'C')
    df_bnp_2['Amount'] = df_bnp_2['Amount'].astype(str).str.replace('-','').astype(float)
    df_bnp_2['Tags'] = 'Others'

    # Wrangling descriptions
    df_bnp_2.loc[df_bnp_2['Type'].str.contains("BLIK - transakcja internetowa", case=False, na=False), 'Tags'] = "Outflow"
    df_bnp_2.loc[df_bnp_2['Type'].str.contains("ExpressElixir otrzymany", case=False, na=False), 'Tags'] = "Inflows"
    df_bnp_2.loc[df_bnp_2['Type'].str.contains("OPŁATA ZA RACHUNEK/PAKIET", case=False, na=False), 'Tags'] = "Inflows"
    df_bnp_2.loc[df_bnp_2['Type'].str.contains("PRZELEW INTERNETOWY", case=False, na=False), 'Tags'] = "Outflow"
    df_bnp_2.loc[df_bnp_2['Type'].str.contains("PRZELEW OTRZYMANY", case=False, na=False), 'Tags'] = "Inflows"
    df_bnp_2.loc[df_bnp_2['Type'].str.contains("TRANS.BEZGOT.KARTĄ DEBET. ", case=False, na=False), 'Tags'] = "Outflow"

    #df_bnp_2.loc[df_bnp_2['Type'].str.contains("PRZELEW NA TELEFON PRZYCHODZ", case=False, na=False), 'Type'] = "Inflow"
    #df_bnp_2.loc[df_bnp_2['Type'].str.contains("PRZELEW ZAKUP BILETU", case=False, na=False), 'Type'] = "Commute"
    #df_bnp_2.loc[df_bnp_2['Type'].str.contains("ZAKUP PRZY UŻYCIU KARTY", case=False, na=False), 'Type'] = "Outflow"
    #df_bnp_2.loc[df_bnp_2['Type'].str.contains("WYPŁATA W BANKOMACIE", case=False, na=False), 'Type'] = "Outflow"
    #df_bnp_2.loc[df_bnp_2['Type'].str.contains("WYPŁATA", case=False, na=False), 'Type'] = "Outflow"
    #df_bnp_2.loc[df_bnp_2['Type'].str.contains("WPŁATA", case=False, na=False), 'Type'] = "Inflow"
    #df_bnp_2.loc[df_bnp_2['Type'].str.contains("OPŁATA - PRZELEW NATYCH. WYCH.", case=False, na=False), 'Type'] = "Outflow"
    #df_bnp_2.loc[df_bnp_2['Type'].str.contains("KAPIT.ODSETEK KARNYCH-OBCIĄŻENIE", case=False, na=False), 'Type'] = "Outflow"

    

    df_bnp_2.loc[df_bnp_2['Desc'].str.contains(pattern_food, case=False, na=False), 'Tags'] = 'Food'
    df_bnp_2.loc[df_bnp_2['Desc'].str.contains(pattern_home, case=False, na=False), 'Tags'] = 'House appliencies'
    df_bnp_2.loc[df_bnp_2['Desc'].str.contains(pattern_beauty, case=False, na=False), 'Tags'] = 'Beauty'
    df_bnp_2.loc[df_bnp_2['Desc'].str.contains(pattern_commute, case=False, na=False), 'Tags'] = 'Commute'
    df_bnp_2.loc[df_bnp_2['Desc'].str.contains(pattern_clothing, case=False, na=False), 'Tags'] = 'Clothing'
    df_bnp_2.loc[df_bnp_2['Desc'].str.contains(pattern_outting, case=False, na=False), 'Tags'] = 'Outting'
    df_bnp_2.loc[df_bnp_2['Desc'].str.contains(pattern_necessity, case=False, na=False), 'Tags'] = 'Necessities'
    df_bnp_2.loc[df_bnp_2['Desc'].str.contains(pattern_hobby, case=False, na=False), 'Tags'] = 'Hobby'
    df_bnp_2.loc[df_bnp_2['Desc'].str.contains(pattern_salary, case=False, na=False), 'Tags'] = 'Salary'
    df_bnp_2.loc[df_bnp_2['Desc'].str.contains(pattern_rent, case=False, na=False), 'Tags'] = 'Rent'
    df_bnp_2.loc[df_bnp_2['Desc'].str.contains(pattern_savings, case=False, na=False), 'Tags'] = 'Savings'
    df_bnp_2.loc[df_bnp_2['Desc'].str.contains(pattern_travel, case=False, na=False), 'Tags'] = 'Travel'
    df_bnp_2 = df_bnp_2.loc[:,['Date','Desc','Amount','Run_balance','Tags']]
  
  if len(df_bnp) != 0:
    # Correctly changing the amount and running balance
    df_bnp[[7,8,9]] = df_bnp[7].str.replace(' ','').str.split(',',n=4, expand=True)
    df_bnp[7] = df_bnp[7].str[:] +','+ df_bnp[8].str[:2]
    df_bnp[8] = df_bnp[8].str[2:] +','+ df_bnp[9].str[:]
    df_bnp = df_bnp.iloc[:,:9]

    # sorting by correctly formated date
    df_bnp[0] = pd.to_datetime(df_bnp[0], format ="%d.%m.%Y")
    df_bnp = df_bnp.sort_values(by=0)
    df_bnp.reset_index(drop=True, inplace=True)

    # dropping unnecessary columns
    df_bnp = df_bnp.iloc[:,[0,1,4,5,7,8]]

    # renaming columns
    df_bnp.columns = ['Date','Desc','Type','Topic','Amount','Run_balance']

    # changing type of the columns
    df_bnp['Amount_v2'] = df_bnp['Amount']
    df_bnp['Amount'] = df_bnp['Amount'].str.replace(',','.').astype(float)
    df_bnp['Run_balance'] = df_bnp['Run_balance'].str.replace(',','.').astype(float)

    # Credit / Debit
    df_bnp['C/D'] = np.where(df_bnp['Amount'] > 0, 'D', 'C')

    df_bnp['Tags'] = 'Others'

    # Wrangling descriptions
    df_bnp.loc[df_bnp['Type'].str.contains("WYMIANA W KANTORZE", case=False, na=False), 'Tags'] = "FX_exchange"
    df_bnp.loc[df_bnp['Type'].str.contains("PRZELEW PRZYCH. SYSTEMAT. WPŁYW", case=False, na=False), 'Tags'] = "Inflow"
    df_bnp.loc[df_bnp['Type'].str.contains("PRZELEW PRZYCHODZĄCY", case=False, na=False), 'Tags'] = "Inflow"
    df_bnp.loc[df_bnp['Type'].str.contains("WPŁATA GOTÓWKI WE WPŁATOMACIE", case=False, na=False), 'Tags'] = "Inflow"
    df_bnp.loc[df_bnp['Type'].str.contains("PRZELEW NATYCHMIASTOWY", case=False, na=False), 'Tags'] = "Inflow"
    df_bnp.loc[df_bnp['Type'].str.contains("PRZELEW WYCHODZĄCY", case=False, na=False), 'Tags'] = "Outflow"
    df_bnp.loc[df_bnp['Type'].str.contains("PRZELEW NA TELEFON WYCHODZĄCY ", case=False, na=False), 'Tags'] = "Outflow"
    df_bnp.loc[df_bnp['Type'].str.contains("PRZELEW NA TELEFON PRZYCHODZ", case=False, na=False), 'Tags'] = "Inflow"
    df_bnp.loc[df_bnp['Type'].str.contains("PRZELEW ZAKUP BILETU", case=False, na=False), 'Tags'] = "Commute"
    df_bnp.loc[df_bnp['Type'].str.contains("ZAKUP PRZY UŻYCIU KARTY", case=False, na=False), 'Tags'] = "Outflow"
    df_bnp.loc[df_bnp['Type'].str.contains("WYPŁATA W BANKOMACIE", case=False, na=False), 'Tags'] = "Outflow"
    df_bnp.loc[df_bnp['Type'].str.contains("WYPŁATA", case=False, na=False), 'Tags'] = "Outflow"
    df_bnp.loc[df_bnp['Type'].str.contains("WPŁATA", case=False, na=False), 'Tags'] = "Inflow"
    df_bnp.loc[df_bnp['Type'].str.contains("OPŁATA - PRZELEW NATYCH. WYCH.", case=False, na=False), 'Tags'] = "Outflow"
    df_bnp.loc[df_bnp['Type'].str.contains("KAPIT.ODSETEK KARNYCH-OBCIĄŻENIE", case=False, na=False), 'Tags'] = "Outflow"

    df_bnp.loc[df_bnp['Type'].str.contains(pattern_food, case=False, na=False), 'Tags'] = 'Food'
    df_bnp.loc[df_bnp['Type'].str.contains(pattern_home, case=False, na=False), 'Tags'] = 'House appliencies'
    df_bnp.loc[df_bnp['Type'].str.contains(pattern_beauty, case=False, na=False), 'Tags'] = 'Beauty'
    df_bnp.loc[df_bnp['Type'].str.contains(pattern_commute, case=False, na=False), 'Tags'] = 'Commute'
    df_bnp.loc[df_bnp['Type'].str.contains(pattern_clothing, case=False, na=False), 'Tags'] = 'Clothing'
    df_bnp.loc[df_bnp['Type'].str.contains(pattern_outting, case=False, na=False), 'Tags'] = 'Outting'
    df_bnp.loc[df_bnp['Type'].str.contains(pattern_necessity, case=False, na=False), 'Tags'] = 'Necessities'
    df_bnp.loc[df_bnp['Type'].str.contains(pattern_hobby, case=False, na=False), 'Tags'] = 'Hobby'
    df_bnp.loc[df_bnp['Type'].str.contains(pattern_salary, case=False, na=False), 'Tags'] = 'Salary'
    df_bnp.loc[df_bnp['Type'].str.contains(pattern_rent, case=False, na=False), 'Tags'] = 'Rent'
    df_bnp.loc[df_bnp['Type'].str.contains(pattern_savings, case=False, na=False), 'Tags'] = 'Savings'
    df_bnp.loc[df_bnp['Type'].str.contains(pattern_travel, case=False, na=False), 'Tags'] = 'Travel'
    df_bnp.loc[df_bnp['Amount'] > 0, 'Tags'] = 'Inflows'

    df_bnp['Amount_v2'] = df_bnp['Amount_v2'].str.replace('-','').str.replace(',','.').astype(float)
    df_bnp = df_bnp.loc[:,['Date','Desc','Run_balance','Amount_v2','Tags']]
    df_bnp.rename(columns={'Amount_v2':'Amount'}, inplace=True)

  if len(df_sant) != 0:
    df_sant['Tags'] = 'Inflows'
    df_sant[2] = df_sant[2].astype(str)

    # Wrangling descriptions
    df_sant.loc[df_sant[4].str.contains("WYMIANA W KANTORZE", case=False, na=False), 4] = "FX_exchange"
    df_sant.loc[df_sant[4].str.contains("PRZELEW PRZYCH. SYSTEMAT. WPŁYW", case=False, na=False), 4] = "Inflow"
    df_sant.loc[df_sant[4].str.contains("PRZELEW PRZYCHODZĄCY", case=False, na=False), 4] = "Inflow"
    df_sant.loc[df_sant[4].str.contains("WPŁATA GOTÓWKI WE WPŁATOMACIE", case=False, na=False), 4] = "Inflow"
    df_sant.loc[df_sant[4].str.contains("PRZELEW NATYCHMIASTOWY", case=False, na=False), 4] = "Inflow"
    df_sant.loc[df_sant[4].str.contains("PRZELEW WYCHODZĄCY", case=False, na=False), 4] = "Outflow"
    df_sant.loc[df_sant[4].str.contains("PRZELEW NA TELEFON WYCHODZĄCY ", case=False, na=False), 4] = "Outflow"
    df_sant.loc[df_sant[4].str.contains("PRZELEW NA TELEFON PRZYCHODZ", case=False, na=False), 4] = "Inflow"
    df_sant.loc[df_sant[4].str.contains("PRZELEW ZAKUP BILETU", case=False, na=False), 4] = "Commute"
    df_sant.loc[df_sant[4].str.contains("ZAKUP PRZY UŻYCIU KARTY", case=False, na=False), 4] = "Outflow"
    df_sant.loc[df_sant[4].str.contains("WYPŁATA W BANKOMACIE", case=False, na=False), 4] = "Outflow"
    df_sant.loc[df_sant[4].str.contains("WYPŁATA", case=False, na=False), 4] = "Outflow"
    df_sant.loc[df_sant[4].str.contains("WPŁATA", case=False, na=False), 4] = "Inflow"
    df_sant.loc[df_sant[4].str.contains("OPŁATA - PRZELEW NATYCH. WYCH.", case=False, na=False), 4] = "Outflow"
    df_sant.loc[df_sant[4].str.contains("KAPIT.ODSETEK KARNYCH-OBCIĄŻENIE", case=False, na=False), 4] = "Outflow"

    df_sant.loc[df_sant[4].str.contains('-', case=False, na=False), 'Tags'] = 'Outflows'
    df_sant.loc[df_sant[2].str.contains(pattern_food, case=False, na=False), 'Tags'] = 'Food'
    df_sant.loc[df_sant[2].str.contains(pattern_home, case=False, na=False), 'Tags'] = 'House appliencies'
    df_sant.loc[df_sant[2].str.contains(pattern_beauty, case=False, na=False), 'Tags'] = 'Beauty'
    df_sant.loc[df_sant[2].str.contains(pattern_commute, case=False, na=False), 'Tags'] = 'Commute'
    df_sant.loc[df_sant[2].str.contains(pattern_clothing, case=False, na=False), 'Tags'] = 'Clothing'
    df_sant.loc[df_sant[2].str.contains(pattern_outting, case=False, na=False), 'Tags'] = 'Outting'
    df_sant.loc[df_sant[2].str.contains(pattern_necessity, case=False, na=False), 'Tags'] = 'Necessities'
    df_sant.loc[df_sant[2].str.contains(pattern_hobby, case=False, na=False), 'Tags'] = 'Hobby'
    df_sant.loc[df_sant[2].str.contains(pattern_salary, case=False, na=False), 'Tags'] = 'Salary'
    df_sant.loc[df_sant[2].str.contains(pattern_rent, case=False, na=False), 'Tags'] = 'Rent'
    df_sant.loc[df_sant[2].str.contains(pattern_savings, case=False, na=False), 'Tags'] = 'Savings'
    df_sant.loc[df_sant[2].str.contains(pattern_travel, case=False, na=False), 'Tags'] = 'Travel'
    df_sant.loc[df_sant['Tags'].str.contains('Outflows', case=False, na=False), 'Tags'] = 'Others'
    # adjusting the columns type
    df_sant[0] = pd.to_datetime(df_sant[0])

    df_sant[1] = df_sant.iloc[:,1].str.replace('Value date: ','')
    df_sant[1] = pd.to_datetime(df_sant[1])

    df_sant[3] = df_sant[3].astype(float)
    df_sant[4] = df_sant[4].str.replace('-','')
    df_sant[4] = df_sant[4].astype(float)

    df_sant.reset_index(drop=True, inplace=True)

    for i in df_sant[df_sant[4]>10000].index:
        df_sant.iloc[i,4] = float(df_sant.iloc[i,2][-6:])

    # dropping unnecessary columns
    df_sant = df_sant.iloc[:,[0,2,3,4,5]]

    # renaming columns
    df_sant.columns = ['Date','Desc','Run_balance','Amount','Tags']

    # after this date we no longer using this bank
    df_sant = df_sant[df_sant['Date'] <= pd.to_datetime('2024-09-05')]
    df_sant = df_sant[::-1]

    # altering the DataFrame
    df_sant = df_sant[['Date', 'Desc', 'Run_balance', 'Amount','Tags']]

  # Past data
  if 'final_output.csv' in listdir(processed_files):
    df_past = pd.read_csv(f'{processed_files}'+'/final_output.csv')
    os.remove(f'{processed_files}'+'/final_output.csv')
    df_past = fixing_type(df_past)
    if len(df_pko) != 0:
      df = pd.concat([df_pko,df_past]).sort_values(by='Date')
    elif len(df_bnp) != 0:
      df = pd.concat([df_bnp,df_past]).sort_values(by='Date')
    elif len(df_bnp_2) != 0:
      df = pd.concat([df_bnp_2,df_past]).sort_values(by='Date')
    elif len(df_sant) != 0:
      df = pd.concat([df_sant,df_past]).sort_values(by='Date')
    df.drop_duplicates(inplace=True)
    df.to_csv((f'{processed_files}'+'/final_output.csv'), index=False)
  
  # No past data
  else:
    if len(df_pko) != 0:
      df_pko.drop_duplicates(inplace=True)
      df_pko.to_csv((f'{processed_files}'+'/final_output.csv'), index=False)
    elif len(df_bnp) != 0:
      df_bnp.drop_duplicates(inplace=True)
      df_bnp.to_csv((f'{processed_files}'+'/final_output.csv'), index=False)
    elif len(df_bnp_2) != 0:
      df_bnp_2.drop_duplicates(inplace=True)
      df_bnp_2.to_csv((f'{processed_files}'+'/final_output.csv'), index=False)
    elif len(df_sant) != 0:
      df_sant.drop_duplicates(inplace=True)
      df_sant.to_csv((f'{processed_files}'+'/final_output.csv'), index=False)
    return 

#### Fixing Type ########################################################################################################################################################
def fixing_type(your_df):
  your_df['Date'] = pd.to_datetime(your_df['Date'])
  #your_df['Trans. type'] = your_df['Trans. type'].astype(str)
  your_df['Run_balance'] = your_df['Run_balance'].replace(" ","",regex=True).replace(',','.', regex=True).astype(float)
  your_df['Amount'] = your_df['Amount'].replace(" ","",regex=True).replace(',','.',regex=True).astype(float)
  your_df['Desc'] = your_df['Desc'].astype(str)
  your_df['Tags'] = your_df['Tags'].astype(str)
  your_df = your_df.sort_values('Date')
  return your_df

#### Streamlit Uploaded Files ###########################################################################################################################################

def streamlit_uploaded_file(uploaded_file):
    with open(os.path.join(f"Data/{st.session_state.role_}/Loaded",uploaded_file.name),"wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("File Saved")

#### Loading user csv files #############################################################################################################################################

def csv_user_load():
    path_to_user_loaded_files = f'Data/{st.session_state.role_}/Loaded'
    archive_path = f'Data/{st.session_state.role_}/Archived'
    processed_files = f'Data/{st.session_state.role_}/Processed'

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

#### Loading user pdf files #############################################################################################################################################

def pdf_user_load():
    if len(os.listdir(f'Data/{st.session_state.role_}/Loaded')) == 0:
       return pd.read_csv(f'Data/{st.session_state.role_}/Processed/final_output.csv')
    path_to_user_loaded_files = f'Data/{st.session_state.role_}/Loaded'
    archive_path = f'Data/{st.session_state.role_}/Archived'
    processed_files = f'Data/{st.session_state.role_}/Processed'

    df_main = pd.DataFrame()

    for index, file_name in enumerate(os.listdir(path_to_user_loaded_files)):
        if '.pdf' in file_name:
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
    return df_main #, loaded_date