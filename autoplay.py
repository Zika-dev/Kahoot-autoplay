from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from configparser import ConfigParser
from getpass import getpass
import os
import re
from time import sleep

chrome_options = Options() 
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument('log-level=3')
PATH = '/driver/chromedriver.exe'
driver = webdriver.Chrome(PATH, options=chrome_options)
config = ConfigParser()

os.system('cls')
driver.get('https://create.kahoot.it/discover')

# Find kahoot
failed = 0

try:
    f = open('login.ini', "r")
except:
    print('Login not found!')
    email = input('Enter kahoot email: ')
    passwrd = getpass('Enter kahoot password: ')
    config['LOGIN'] = {
    'email': email,
    'password': passwrd
    }
    with open('login.ini', 'w') as f:
        config.write(f)
    config.set('LOGIN', 'email', email)
    config.set('LOGIN', 'password', passwrd)
    sleep(1)

os.system('cls')
print('Email and password loaded')
config.read('login.ini')
email = config.get('LOGIN', 'email')
passwrd = config.get('LOGIN', 'password')

while True:
    url_or_name = input('Search by kahoot url or name? ')
    if url_or_name == 'url':
        kahoot_url = input('Enter url of kahoot: ')
        break
    elif url_or_name == 'name':
        name = input('Enter name of kahoot: ')
        break
    else:
        print('That is not a valid option!')

username = driver.find_element(By.ID,'username')
username.send_keys(email)

password = driver.find_element(By.ID, 'password')
password.send_keys(passwrd)

enter = driver.find_element(By.ID, 'login-submit-btn')
enter.send_keys(Keys.RETURN)
pageLoaded = False
while pageLoaded == False:
    try:
        search = WebDriverWait(driver, 0.1).until(EC.presence_of_element_located((By.XPATH, '//*[@id="main-content"]/div/div/div/div[1]/div[2]/div/div/input')))
    except TimeoutException:
        if failed >= 30:
            print('Timeout. Either the login failed or you need to change the timeout threshold if your internet is slow')
            quit()
        failed=failed+1
        print('Waiting for page to load ...')
    else:
        pageLoaded = True
if url_or_name =='name':
    get = driver.find_element(By.XPATH, '//*[@id="main-content"]/div/div/div/div[1]/div[2]/div/div/input')
    get.send_keys(name)
    get.send_keys(Keys.RETURN)
    ### Change if internet is slow ###
    sleep(2)
    ##################################
    kahoot = driver.find_element(By.XPATH, '//*[@id="main-content"]/div/div/div/div[3]/div[1]/div/a').click()
    url = driver.current_url
    os.system('cls')
    print(f"Kahoot url: {url}")
    driver.get(url)
elif url_or_name =='url':
    driver.get(kahoot_url)
    os.system('cls')


# Get answers
print('Getting answers...')
sleep(1)
try:
    driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div/main/div[2]/div[2]/div[2]/div/section[1]/div[1]/button').click()
except:
    print('Unable to fetch answers. Does the kahoot require Kahoot!+?')
    quit()

div1 = 1
div2 = 1
failed = 0
question = 1
last_question = 0
answers = []

while True:
    try:
        answer = driver.find_element(By.XPATH, f'//*[@id="root"]/div/div/div/main/div[2]/div[2]/div[2]/div/section[1]/div[2]/div[{div2}]/div/div[2]/div[{div1}]').get_attribute('aria-label')
        div1 = div1+1
        if re.search(r"\bcorrect\b", answer):
            if (last_question != question):
                print(f"Question: {question}")
                last_question = question
                option = answer[0:8]
                add = ([int(s) for s in option.split() if s.isdigit()])
                answers.append(add)
            print(answer + "\n")
    except:
        if failed >= 10:
            print(answers)
            while True:
                url_or_name = input('Enable autoplay? ')
                if url_or_name == 'y':
                    game_pin = input('Enter game pin: ')
                    playerName = input('Enter player name: ')
                    print('Creating player...')

                    driver.get('https://kahoot.it/')
                    pin = driver.find_element(By.ID, 'game-input')
                    pin.send_keys(game_pin)
                    pin.send_keys(Keys.RETURN)
                    pageLoaded=False
                    while pageLoaded == False:
                        try:
                            nickname = WebDriverWait(driver, 0.1).until(EC.presence_of_element_located((By.ID, 'nickname')))
                        except TimeoutException:
                            print('Waiting for kahoot to load...')
                        else:
                            pageLoaded = True
                    nickname = driver.find_element(By.ID, 'nickname')
                    nickname.send_keys(playerName)
                    nickname.send_keys(Keys.RETURN)

                    print('Player entered successfully')

                    x=0
                    while True:
                        pageLoaded = False
                        while pageLoaded == False:
                            try:
                                guess = WebDriverWait(driver, 0.1).until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div[1]/div/div/main/div[2]/div/div/button[1]')))
                            except TimeoutException:
                                print('Waiting for next question...')
                            else:
                                driver.find_element(By.XPATH, f'//*[@id="root"]/div[1]/div/div/main/div[2]/div/div/button{answers[x]}').click()
                                print(f'Answer is {answers[x]}')
                                x=x+1
                                if x >= len(answers):
                                    print('Finished!')
                                    quit()
                                    
                elif url_or_name == 'n':
                    print('Quitting program...')
                    quit()
                else:
                    print('That is not a valid option!')
        failed = failed+1
        div1=1
        div2=div2+1
        question=question+1
    else:
        failed = 0