import time
import pandas as pd
import requests
import re
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup, element
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from concurrent.futures import ThreadPoolExecutor

# Set up Chrome options (optional)
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("--headless")  # Run in headless mode (optional)
#options.add_argument("--no-sandbox")
#options.add_argument("--disable-dev-shm-usage")
# Use a proper Service object
service = Service(ChromeDriverManager().install())

import pages.real_estates as res

def gratka(user_choice_option_1, user_choice_option_3):
    # Set up Chrome options (optional)
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # Use a proper Service object
    service = Service(ChromeDriverManager().install())

    ### 1 Step
    # Opening Google
    driver = webdriver.Chrome(service=service, options=options)
    # Direct to predefine website
    driver.get('https://gratka.pl')

    ### 1.5 Step
    # Accespting cookies
    time.sleep(7)
    #cookie = driver.find_element(By.XPATH, '/html/body/div[7]/div/div[2]/div/div[6]/button[2]')
    cookie = driver.find_element(By.XPATH, '/html/body/div[8]/div/div[2]/div/div[6]/button[2]')
    cookie.click()
    time.sleep(1)

    ### 2 Step
    ## Choose between buy or rent
    ## Default is buy so in case of rent then change
    if user_choice_option_1  == 'Mieszkanie na wynajem' or user_choice_option_1  == 'Flats for rent':
        buy_or_rent_dropdown = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/main/div[1]/div/div[2]/div/div/div[1]/div/button/img')
        buy_or_rent_dropdown.click()
        time.sleep(1)
        rent_button = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/main/div[1]/div/div[2]/div/div/div[1]/div/div/div/div/button[2]')
        rent_button.click()
        time.sleep(1)
        # after choosing proper option the dropdown closes by itslef

    if user_choice_option_1 == 'Domy na sprzedaż' or user_choice_option_1 == 'Houses for sale':
        house = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/main/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/button[2]')
        house.click()
        time.sleep(1)
    elif user_choice_option_1 == 'Działki na sprzedaż' or user_choice_option_1 == 'Lands for sale':
        land = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/main/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/button[4]')
        land.click()
        time.sleep(1)

    ## Location search box
    loc_bar = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/main/div[1]/div/div[2]/div/div/div[3]/div/div/div[1]/div/div/div/input')
    time.sleep(2)
    loc_bar.send_keys(user_choice_option_3) #variable
    time.sleep(1)
    loc_bar.send_keys(Keys.ENTER)

    search_button = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/main/div[1]/div/div[2]/div/div/div[4]/div[2]/div/button')
    search_button.click()
    time.sleep(3)
    search_button.click()
    time.sleep(5)
    ### 4 Iterate through houses
    soup1 = BeautifulSoup(driver.page_source, 'html.parser')
    #df = pd.DataFrame()
    estates = []

    number_of_pages = int(soup1.find('div', {'class': 'pagination'}).text.split('...')[1].split('Nas')[0])
    for i in range(0,number_of_pages-1):
        # 1st Part of Same Website Issue
        if i > 2:
            current_page = int(driver.current_url.split('=')[1])
            if current_page == past_page:
                time.sleep(5)
                force_next_page = (driver.current_url.split('=')[0]) + "=" + f"{current_page + 1}"
                driver.get(force_next_page)
                time.sleep(2)

        # web scrap
        soup1 = BeautifulSoup(driver.page_source, 'html.parser')
        propertes = soup1.find_all('div', {'class':'card card--bottom-margin'})
        time.sleep(1)
        for property in propertes:
            try:
                price = int(property.find('div',{'class':'property-card__price'}).text.replace(" ","").split('zł')[0])
            except:
                price = np.nan

            try:
                price_per_m2 = int(property.find('div',{'class':'property-card__price'}).text.replace(" ","").split('zł')[1])
            except:
                price_per_m2 = np.nan

            try:
                sqrmeter = property.text.split('Zobacz opis')[0].split('zł/m²')[1].split('•')[0]
            except:
                sqrmeter = np.nan

            try:
                rooms = property.text.split('Zobacz opis')[0].split('zł/m²')[1].split('•')[1]
            except:
                rooms = np.nan

            try:
                floor = property.text.split('Zobacz opis')[0].split('zł/m²')[1].split('•')[2]
            except:
                floor = np.nan
            
            try:
                link = 'https://gratka.pl' + property.find('a', {'class':'property-card'})['href']
            except:
                link = np.nan

            estates.append({
                'title' : property.find('div',{'class':'property-card__title'}).text.split('\n'),
                'location' :property.find('div',{'class':'property-card__location'}).text.split('\n'),
                'price': price,            
                'price_per_m2' : price_per_m2,
                'sqrmeter': sqrmeter,
                'rooms': rooms,
                'floor': floor,
                'link' : link,
                'page': i 
            })

        # 2nd Part of Same Website Issue
        if i > 0:
            past_page = int(driver.current_url.split('=')[1])
        
        # dealing with pop-outs
        try:
            popout = driver.find_element(By.XPATH, '/html/body/div/div/div/div/div[1]/svg')
        except NoSuchElementException:
            popout = None
        
        if popout != None:
            driver.get(current_page)
            time.sleep(2)
        next_page = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/main/div/section/div[2]/div/div[3]/a/div')
        try:
            next_page.click()
        except ElementClickInterceptedException:
            driver.get(current_page)
            time.sleep(2)
            next_page.click()
        time.sleep(2)

    # Data cleaning
    df_gratka = pd.DataFrame(estates)

    df_gratka['sqrmeter'] = df_gratka['sqrmeter'].str.split(' ', n=1, expand=True)[0]
    df_gratka[['street','district']] = df_gratka['location'].str[0].str.split(',', expand=True)[[0,1]]
    df_gratka['rooms'] = df_gratka['rooms'].str.split(' ', expand=True)[0]


    df_gratka.drop(columns=['location'], inplace=True)
    df_gratka[['floor','max_floor']] = df_gratka['floor'].str.replace('piętro',"").str.replace('parter','0').str.split('/',expand=True)
    df_gratka.title = df_gratka.title.str[0]
    df_gratka.district = df_gratka.district.str.strip()
    return df_gratka

def olx(user_choice_option_1, user_choice_option_3):
    ### 1 Step
    # Opening Google
    driver = webdriver.Chrome(service=service, options=options)
    # Direct to predefine website
    driver.get('https://olx.pl/')
    time.sleep(1)

    ### Step 1.1
    ## Accepting cookies
    cookies =  driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/div[1]/div/div[2]/div/button[1]')
    cookies.click()
    time.sleep(2)

    ### Step 1.2
    ## Opening main category
    estates = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[3]/div[2]/div/div/div/a[5]')
    estates.click()
    time.sleep(1)

    ### Step 1.3
    ## opening specific category
    if user_choice_option_1 == 'Domy na sprzedaż' or user_choice_option_1 == 'Houses for sale':
        estate_cat = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[3]/div[2]/div/div/div/div[3]/div/div/a[2]')
    elif user_choice_option_1 == 'Działki na sprzedaż' or user_choice_option_1 == 'Lands for sale':
        estate_cat = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[3]/div[2]/div/div/div/div[3]/div/div/a[3]')
    else: # flats as default
        estate_cat = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[3]/div[2]/div/div/div/div[3]/div/div/a[1]')
    time.sleep(1)
    estate_cat.click()
    time.sleep(6)

    ### Step 1.4
    ## Search Location
    loc_bar = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[3]/form/div[1]/div[2]/div/div/div/div/div/input')
    loc_bar.click()
    loc_bar.send_keys(user_choice_option_3) # variable
    time.sleep(2)
    choose_first_option = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[3]/form/div[1]/div[2]/div/div/div[2]/div[1]')
    choose_first_option.click()
    time.sleep(2)

    ### Step 1.5
    ## Rent or buy
    rent_or_buy = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[3]/form/div[3]/div[1]/div/div[2]/div/div/button')
    rent_or_buy.click()
    if user_choice_option_1 == 'Mieszkanie na wynajem' or user_choice_option_1 == 'Flats for rent':
        rent_ = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[3]/form/div[3]/div[1]/div/div[2]/div/div/div/div[1]/button[2]')
        rent_.click()
    else:
        buy_ = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[3]/form/div[3]/div[1]/div/div[2]/div/div/div/div[1]/button[3]')
        buy_.click()
    time.sleep(1) 

    # scroll to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

    max_page_number = int(driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[3]/form/div[6]/div/section[1]/div/ul/li[5]/a').text)

    estates = []

    for page in range(0,max_page_number-1):
        # page content
        soup1 = BeautifulSoup(driver.page_source, 'html.parser')
        properties = soup1.find_all('div', {'class':'css-1sw7q4x'})
        for property in properties:
            try:
                price = int(property.find('p', {'class':"css-blr5zl"}).text.split('zł')[0].replace(' ',''))
            except:
                price = np.nan

            try:
                price_per_m2 = float(property.find('span', {'class':"css-h59g4b"}).text.split(' - ')[1].split(' ')[0].replace(',','.'))
            except:
                price_per_m2 = np.nan

            try:
                sqrmeter = float(property.find('span', {'class':"css-h59g4b"}).text.split(' - ')[0].split(' ')[0].replace(',','.'))
            except:
                sqrmeter = np.nan
            
            try:
                link = ('olx.pl' + property.find('a', {'class':"css-1tqlkj0"})['href'])
            except:
                link = np.nan
            
            try:
                location = property.find('p', {'class':"css-1b24pxk"}).text.split('-')[0].split(', ')[1].strip()
            except:
                location = np.nan
            
            try:
                title = property.find('h4', {'class':"css-hzlye5"}).text
            except:
                title = np.nan

            estates.append({
                'title' : title, # done
                'location' : location, # done
                'price': price, # done            
                'price_per_m2' : price_per_m2, # done
                'sqrmeter': sqrmeter, # done
                'link' : link, # done
                'page': page
            })

        # next page
        if page == 0:
            driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[3]/form/div[6]/div/section[1]/div/ul/a').click()
        else:
            try:
                driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[3]/form/div[6]/div/section[1]/div/ul/a[2]').click()
            except:
                driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[2]/form/div[6]/div/section[1]/div/ul/a[2]').click()
        time.sleep(5)
    return pd.DataFrame(estates).drop_duplicates().dropna()

def otodom(user_choice_option_1, user_choice_option_3):
    ### 1 Step
    # Opening Google
    driver = webdriver.Chrome(service=service, options=options)
    # Direct to predefine website
    driver.get('https://otodom.pl/')
    # Wait
    time.sleep(4)
    cookie_click = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/div[1]/div/div[2]/div/button[1]')
    cookie_click.click()
    time.sleep(2)

    # Click to see options
    driver.find_element(By.XPATH, '/html/body/div[1]/main/section[1]/div/div/form/div/div[1]/div[1]/div[1]/div/div[1]/div/div/div/div/div/button').click()

    # change type of real estate based on user choice
    # nothing - flats
    if user_choice_option_1 == 'Domy na sprzedaż' or user_choice_option_1 == 'Houses for sale':
        driver.find_element(By.XPATH, '/html/body/div[1]/main/section[1]/div/div/form/div/div[1]/div[1]/div[1]/div/div/div[2]/div/div[3]').click()
    elif user_choice_option_1 == 'Działki na sprzedaż' or user_choice_option_1 ==  'Lands for sale':
        driver.find_element(By.XPATH, '/html/body/div[1]/main/section[1]/div/div/form/div/div[1]/div[1]/div[1]/div/div/div[2]/div/div[6]').click()

    time.sleep(2)

    # change rent/buy based on user choice
    # nothing - buy
    if user_choice_option_1 == 'Mieszkanie na wynajem' or user_choice_option_1 == 'Flats for rent':
        driver.find_element(By.XPATH, '/html/body/div[1]/main/section[1]/div/div/form/div/div[1]/div[1]/div[2]/div/div/div[2]/div/div[1]').click()

    time.sleep(2)

    search_bar = driver.find_element(By.XPATH, '/html/body/div[1]/main/section[1]/div/div/form/div/div[1]/div[2]/div[1]/div/label/div/div/input')
    search_bar.click()
    time.sleep(3)
    driver.find_element(By.XPATH, '/html/body/div[1]/main/section[1]/div/div/form/div/div[1]/div[2]/div[1]/div[2]/div/div/label/div/div/input').send_keys(user_choice_option_3)
    time.sleep(1)
    driver.find_element(By.XPATH, '/html/body/div[1]/main/section[1]/div/div/form/div/div[1]/div[2]/div[1]/div[2]/div/div/label/div/div/input').send_keys(Keys.ENTER)
    time.sleep(1)

    # trying to click somewhere to make button clickable
    driver.find_element(By.XPATH, '/html/body/div[1]/main/section[1]/div/div/form/div/div[2]/button').click()
    time.sleep(1)

    # At the end search
    #search_ = driver.find_element(By.XPATH, '/html/body/div[1]/main/section[1]/div/div/form/div/div[2]/button')
    #driver.find_element(By.XPATH, '/html/body/div[1]/main/section[1]/div/div/form/div/div[2]/button').click()
    #search_.click()
    time.sleep(2)

    # changing number of available offer at once to max = 72
    # open menu
    #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #time.sleep(3)
    #driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/main/div/div[2]/div[4]/div[1]/div[1]/div[4]/div[2]/div[2]/div/div/div').click()
    #driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/main/div/div[2]/div[4]/div[1]/div[1]/div[4]/div[2]/div[2]/div/div/div').click()
    #time.sleep(2)
    # choose max
    #driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/main/div/div[2]/div[4]/div[1]/div[1]/div[4]/div[2]/div[2]/div/div/div[2]/div/div[4]').click()
    #time.sleep(1)

    # get number of all pages
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    max_page_number = int(driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/main/div/div[2]/div[4]/div[1]/div[1]/div[4]/div[2]/div[1]/ul/li[7]/button').text)
    # get button for next page
    # next_button = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/main/div/div[2]/div[4]/div[1]/div[1]/div[4]/div[2]/div[1]/ul/li[8]/button')

    estates_ = []

    page_navigation = driver.current_url

    for page in range(1, max_page_number):
        # read website info
        soup1 = BeautifulSoup(driver.page_source)
        propertes = soup1.find_all('div',{'class':'css-1lyza52 e11az2p00'})
        time.sleep(1)

        for property in propertes:
            # price
            try:
                price = int(property.find('span', {'class',"css-ussjv3 eanmlll1"}).text.replace('\xa0','').strip('zł'))
            except:
                price = pd.NA
            # price per m2
            try:
                price_per_m2 = int(property.find('span', {'class',"css-u0t81v eanmlll2"}).text.replace('\xa0','').strip('zł/m²'))
            except:
                price_per_m2 = pd.NA
            # title - join list
            try:
                title = property.find('p', {'class', 'css-135367 e11az2p02'}).text.replace('\xa0','')
            except:
                title = pd.NA
            # dzielica
            try:
                district = property.find('p', {'class', 'css-oxb2ca e1cuc5p50'}).text.split(',')[-3].strip()
            except:
                district = pd.NA
            # miasto
            try:
                town = property.find('p', {'class', 'css-oxb2ca e1cuc5p50'}).text.split(',')[-2].strip()
            except:
                town = pd.NA
            # no. of rooms
            try:
                no_of_rooms = int(property.find('div', {'class', 'css-1jbawm2 e11az2p05'}).text.replace('\xa0','').split('Liczba pokoi')[1].split('pokoje')[0].strip())
            except:
                no_of_rooms = pd.NA
            # sqr meter
            try:
                sqrm = float(property.find('div', {'class', 'css-1jbawm2 e11az2p05'}).text.replace('\xa0','').split('metr kwadratowy')[1].split('m²')[0].strip())
            except:
                sqrm = pd.NA
            # floor
            try:
                floor = ' '.join(property.find('div', {'class', 'css-1jbawm2 e11az2p05'}).text.replace('\xa0','').lower().split('piętro')[1:])
            except:
                floor = pd.NA
            # link
            try:
                link = ('otodom.pl' + property.find('a',{'class','css-16vl3c1 e13tkx7i0'})['href'])
            except:
                link = pd.NA

            estates_.append({
                    'title' : title,
                    'location' : district,
                    'price' : price,            
                    'price_per_m2' : price_per_m2,
                    'sqrmeter' : sqrm,
                    'floor' : floor,
                    'link' : link,
                    'page': page
                })

        # this is to scroll down
        # driver.execute_script("window.scrollTo(1, document.body.scrollHeight);")
        # time.sleep(1)
        # this is to go further
        driver.get(page_navigation.split('?page=')[0] + f'?page={page}')
        time.sleep(1)
    return pd.DataFrame(estates_)