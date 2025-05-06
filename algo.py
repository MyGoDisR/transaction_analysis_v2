import pandas as pd
import numpy as np
from pypdf import PdfReader
from os import listdir # for retrieving
import os
import re
import matplotlib.pyplot as plt
import time
import fitz
import pathlib

def fixing_type(your_df):
  your_df['Date'] = pd.to_datetime(your_df['Date'])
  your_df['Trans. type'] = your_df['Trans. type'].astype(str)
  your_df['Run_balance'] = your_df['Run_balance'].replace(" ","",regex=True).replace(',','.', regex=True).astype(float)
  your_df['Amount'] = your_df['Amount'].replace(" ","",regex=True).replace(',','.',regex=True).astype(float)
  your_df['Desc'] = your_df['Desc'].astype(str)
  your_df['Type'] = your_df['Type'].astype(str)
  your_df = your_df.sort_values('Date')
  return your_df

def data_to_df(folder_path):

  # No new data 
  if len(listdir(folder_path)) == 1 and "Archived" in listdir(folder_path):
    df = pd.read_csv('output.csv', header = 0)
    df.drop_duplicates(inplace=True)
    return df

  # creation of Archived folder
  if "Archived" not in listdir(folder_path):
    os.makedirs(folder_path+"/Archived")

  df = pd.DataFrame()

  for index, file_ in enumerate(listdir(folder_path)):
    if 'Wyciag_' in file_:
      pdfbytes = pathlib.Path(folder_path+'/'+file_).read_bytes()
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
      df = pd.concat([df, pd.DataFrame(context)])
      os.replace(folder_path + '/' + file_, folder_path + '/Archived/' + file_)
      


  df = df.set_axis(['Date','Ref','Trans. type','Amount','Run_balance','Date_2','In-depth Desc.','In-depth Desc._2','In-depth Desc._3','del'], axis=1)
  df['Desc'] = df['In-depth Desc.'].astype(str) + df['In-depth Desc._2'].astype(str) + df['In-depth Desc._3'].astype(str)
  df = df.loc[:,('Date','Ref','Trans. type','Amount','Run_balance','Desc')]

  df.drop_duplicates(inplace=True)

  df['Date'] = pd.to_datetime(df['Date'])
  df['Trans. type'] = df['Trans. type'].astype(str)
  df['Run_balance'] = df['Run_balance'].str.replace(" ","",regex=True).replace(',','.', regex=True).astype(float)
  df['Amount'] = df['Amount'].str.replace(" ","",regex=True).replace(',','.',regex=True).astype(float)
  df['C/D'] = np.where(df['Amount'] > 0, 'D', 'C')
  df['Amount'] = df['Amount'].astype(str).str.replace("-","",regex=True).astype(float)
  df['Desc'] = df['Desc'].astype(str)
  df['Type'] = 'Others'  

  df = df.sort_values('Date')
      
  # Wrangling descriptions
  df.loc[df['Trans. type'].str.contains("WYMIANA W KANTORZE", case=False, na=False), 'Type'] = "FX_exchange"
  df.loc[df['Trans. type'].str.contains("PRZELEW PRZYCH. SYSTEMAT. WPŁYW", case=False, na=False), 'Type'] = "Inflow"
  df.loc[df['Trans. type'].str.contains("PRZELEW PRZYCHODZĄCY", case=False, na=False), 'Type'] = "Inflow"
  df.loc[df['Trans. type'].str.contains("WPŁATA GOTÓWKI WE WPŁATOMACIE", case=False, na=False), 'Type'] = "Inflow"
  df.loc[df['Trans. type'].str.contains("PRZELEW NATYCHMIASTOWY", case=False, na=False), 'Type'] = "Inflow"
  df.loc[df['Trans. type'].str.contains("PRZELEW WYCHODZĄCY", case=False, na=False), 'Type'] = "Outflow"
  df.loc[df['Trans. type'].str.contains("PRZELEW NA TELEFON WYCHODZĄCY ", case=False, na=False), 'Type'] = "Outflow"
  df.loc[df['Trans. type'].str.contains("PRZELEW NA TELEFON PRZYCHODZ", case=False, na=False), 'Type'] = "Inflow"
  #df.loc[df['Trans. type'].str.contains("PRZELEW ZAKUP BILETU", case=False, na=False), 'Type'] = "Commute"
  #df.loc[df['Trans. type'].str.contains("ZAKUP PRZY UŻYCIU KARTY", case=False, na=False), 'Type'] = "Outflow"
  df.loc[df['Trans. type'].str.contains("WYPŁATA W BANKOMACIE", case=False, na=False), 'Type'] = "Outflow"
  df.loc[df['Trans. type'].str.contains("WYPŁATA", case=False, na=False), 'Type'] = "Outflow"
  df.loc[df['Trans. type'].str.contains("WPŁATA", case=False, na=False), 'Type'] = "Inflow"
  df.loc[df['Trans. type'].str.contains("OPŁATA - PRZELEW NATYCH. WYCH.", case=False, na=False), 'Type'] = "Outflow"
  df.loc[df['Trans. type'].str.contains("KAPIT.ODSETEK KARNYCH-OBCIĄŻENIE", case=False, na=False), 'Type'] = "Outflow"
    
  # Assigning Tags to transactions
  # list of shops
  food_shops = ['biedronka','auchan','lidl','kaufland','carrefour','aldi','sklep spozywczy','zabka','STOKROTKA','BAJPIX','DELIKATES','TSS','NETTO','PIEKARNIA',
                'CUKIERNIA','ART. SPOZ','KIOSK','Supermarket','1minute','SMAK','Firma Handlowa','INTERMARCHE','Tchibo','LITTLE INDIA','Duty','Zator','WODNIK',
                'KrakPres','AWITEKS','JMT','ADM24','UL. ELEKTRYCZNA 2/U5','UL. SZEWSKA 27','Kaszubskie','UL. KASZUBSKA','UL. SIKORKI 21A','Al.capone','RUCH',
                'TESCO','DINO','FRESHMARKET','CARERREFOUR EXPRESS','Swiat Alkoholi','MALE MOLO SOPOT','Warszawska Bagieta','EUROSPAR','POLOMARKET','Hale Banacha',
                'Alkohole 24','PIOTR I PAWEL','Piotr i Pawel','Relay','OWOCE WARZYWA','1-Minute','Rolmies','ZIARNA ZYCIA WARSZAWA','Virgin','KERANISS SP. Z O.O. BALICE',
                'FH "Eldomek" Tarnow','AUTOMAT M21 KRAKOW','GRAWITON','SWIEZACZEK','HALIMA ENTERPRISE3282Tarnow','DANIEL BNP']

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

  df.loc[df['Desc'].str.contains(pattern_food, case=False, na=False), 'Type'] = 'Food'
  df.loc[df['Desc'].str.contains(pattern_home, case=False, na=False), 'Type'] = 'House appliencies'
  df.loc[df['Desc'].str.contains(pattern_beauty, case=False, na=False), 'Type'] = 'Beauty'
  df.loc[df['Desc'].str.contains(pattern_commute, case=False, na=False), 'Type'] = 'Commute'
  df.loc[df['Desc'].str.contains(pattern_clothing, case=False, na=False), 'Type'] = 'Clothing'
  df.loc[df['Desc'].str.contains(pattern_outting, case=False, na=False), 'Type'] = 'Outting'
  df.loc[df['Desc'].str.contains(pattern_necessity, case=False, na=False), 'Type'] = 'Necessities'
  df.loc[df['Desc'].str.contains(pattern_hobby, case=False, na=False), 'Type'] = 'Hobby'
  df.loc[df['Desc'].str.contains(pattern_salary, case=False, na=False), 'Type'] = 'Salary'
  df.loc[df['Desc'].str.contains(pattern_rent, case=False, na=False), 'Type'] = 'Rent'
  df.loc[df['Desc'].str.contains(pattern_savings, case=False, na=False), 'Type'] = 'Savings'
  df.loc[df['Desc'].str.contains(pattern_travel, case=False, na=False), 'Type'] = 'Travel'

  # Past data
  if 'output.csv' in listdir():

    df_past = pd.read_csv('output.csv')
    os.remove('output.csv')
    df_past = fixing_type(df_past)
    df = pd.concat([df,df_past]).sort_values(by='Date')
    df.drop_duplicates(inplace=True)

  df.to_csv("output.csv", index=False)

  return df