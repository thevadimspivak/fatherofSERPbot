import telebot
from token_id import token # import your token ID
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import csv
import os

user_agent = ' ' # user-agent

options = Options()
options.add_argument("--headless")
options.add_argument('--incognito')
options.add_argument('--no-sandbox')
options.add_argument('--blink-settings=imagesEnabled=false')
options.add_argument(f'--user-agent={user_agent}')
options.page_load_strategy = 'eager'

s = Service(executable_path="./chromedriver.exe") # Path to chromedriver.exe
driver = webdriver.Chrome(service=s, options=options)

father = telebot.TeleBot(token)
@father.message_handler(commands=['start'])
def start_message(message):
    
    father.send_message(message.chat.id, 'Hello, I am Father of SERP in Google. I am here to help you to get your best searching experience')
    username = str(message.chat.username) 
    father.send_message(message.chat.id, 'Enter your web query')
    

def get_numbers_of_results(query):
    try:
        url = f'https://google.com/search?q={query}&hl=en'
        driver.get(url)
        number_of_results = driver.find_element(By.ID, 'result-stats')
        return number_of_results.text
    except NoSuchElementException:
        print('NoSuch')
        return 'some result'


@father.message_handler(content_types=['text'])
def get_web_query(message):
    global query, csv_name
    query = message.text
    csv_name = query.replace(' ', '_')

    father.send_message(message.chat.id, 'searching... wait for a moment')
    sleep(2)
    response = get_numbers_of_results(query).lower()
    response = response.split(' (')[0]
    father.send_message(message.chat.id, f'There were found {response}')  

    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    key_1 = telebot.types.KeyboardButton(text='~10')
    key_2 = telebot.types.KeyboardButton(text='~20')
    key_3 = telebot.types.KeyboardButton(text='~30')
    key_4 = telebot.types.KeyboardButton(text='~40')
    kb.add(key_1, key_2, key_3, key_4)
    father.send_message(message.chat.id, 'How many results do you need?', reply_markup=kb)
    father.register_next_step_handler(message, keyboard2)

def keyboard2(message):
    global num_of_res
    num_of_res = message.text[1:]
    kb2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    key_d = telebot.types.KeyboardButton(text='desktop')
    key_m = telebot.types.KeyboardButton(text='mobile')
    kb2.add(key_d, key_m)
    father.send_message(message.chat.id, 'What platform do you use?', reply_markup=kb2)
    father.register_next_step_handler(message, sending_csv)

   
def sending_csv(message):
    
    global plat
    plat = message.text
    father.send_message(message.chat.id, 'Ive got CSV data file for you\nPlease wait..', reply_markup = telebot.types.ReplyKeyboardRemove())
  
    if plat == 'desktop':
        get_csv(query, num_of_res)   
        
        doc = open(f'{csv_name}_{num_of_res}.csv', 'rb')
        father.send_document(message.from_user.id, doc)

    elif plat == 'mobile':
        get_csv_mobile(query, num_of_res)    
        
        doc = open(f'{csv_name}_{num_of_res}.csv', 'rb')
        father.send_document(message.from_user.id, doc)

    print(f'{csv_name}_{num_of_res}.csv was sent') 
    doc.close()
    sleep(3)
    os.remove(f'{csv_name}_{num_of_res}.csv')
    father.send_message(message.chat.id, 'Enter another query..')

    

def get_csv(query, num_of_res):
    url = f'https://google.com/search?q={query}&hl=en'

    driver.get(url)
    sleep(3)
    num = 1

    with open(f'{csv_name}_{num_of_res}.csv', 'w', encoding='utf-8-sig') as myfile:
        writer = csv.writer(myfile, delimiter=';', lineterminator='\n')
        writer.writerow(
            ('Number',
            'Title',
            'Link')
            )
        myfile.close()
    num_of_res = int(num_of_res)
    num_of_pages = num_of_res // 10 + 1

    for page in range(1, num_of_pages):
        try:
            element_present = EC.presence_of_element_located((By.CSS_SELECTOR, '.g'))
            WebDriverWait(driver, 10).until(element_present)
        except TimeoutException:
            print('Timed Out')

        search_results = driver.find_elements(By.CSS_SELECTOR, '.g')
        for result in search_results:
            try:
                link = result.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                title = result.find_element(By.CSS_SELECTOR, 'h3').text
            except NoSuchElementException:
                print('No such Element')
            
            with open(f'{csv_name}_{num_of_res}.csv', 'a', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile, delimiter=';', lineterminator='\n')
                writer.writerow(
                    (
                        num,
                        title,
                        link
                    )
                )
            num += 1
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, '#pnnext')
            next_button.click()

        except:
            break
    # driver.quit()

def get_csv_mobile(query, num_of_res):
    url = f'https://google.com/search?q={query}&hl=en'

    driver.get(url)
    sleep(3)
    num = 1

    with open(f'{csv_name}_{num_of_res}.csv', 'w', encoding='utf-8-sig') as myfile:
        writer = csv.writer(myfile, lineterminator='\n')
        writer.writerow(
            ('Number',
            'Title',
            'Link')
            )
        myfile.close()

    num_of_res = int(num_of_res)
    num_of_pages = num_of_res // 10 + 1

    for page in range(1, num_of_pages):
        try:
            element_present = EC.presence_of_element_located((By.CSS_SELECTOR, '.g'))
            WebDriverWait(driver, 10).until(element_present)
        except TimeoutException:
            print('Timed Out')

        search_results = driver.find_elements(By.CSS_SELECTOR, '.g')
        for result in search_results:
            try:
                link = result.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                title = result.find_element(By.CSS_SELECTOR, 'h3').text
            except NoSuchElementException:
                print('No such Element')
                      
            with open(f'{csv_name}_{num_of_res}.csv', 'a', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile, lineterminator='\n')
                writer.writerow(
                    (
                        num,
                        title,
                        link
                    )
                )
            num += 1
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, '#pnnext')
            next_button.click()

        except:
            break
    # driver.quit()


father.infinity_polling()
