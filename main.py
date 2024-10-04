import os
import requests
from time import sleep
from configparser import ConfigParser
from os import system, name
from threading import Thread, active_count
import csv
import phonenumbers
from phonenumbers import PhoneNumber, PhoneNumberFormat
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from bs4 import BeautifulSoup
import random
from emailtools import generate

software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value, SoftwareName.EDGE.value, SoftwareName.OPERA.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value, OperatingSystem.MAC.value]

user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=1200)

THREADS = 600
PROXIES_TYPES = ('http', 'socks4', 'socks5')

errors = open('errors.txt', 'a+')

time_out = 15
success_count = 0
error_count = 0
username = ""

def generate_random_phone_number():
    while True:
        country_code = "+{}".format(random.randint(1, 999))
        national_number = str(random.randint(1000000000, 9999999999))
        phone_number_str = country_code + national_number
        try:
            phone_number = phonenumbers.parse(phone_number_str)
            if phonenumbers.is_valid_number(phone_number):
                return phonenumbers.format_number(phone_number, PhoneNumberFormat.E164)
        except phonenumbers.phonenumberutil.NumberParseException:
            continue

def get_random_line(filename, username):
    with open(filename, 'r') as file:
        lines = file.readlines()
        line = random.choice(lines).strip()
        return line.replace('{username}', username)

def control(proxy, proxy_type, username):
    
    global success_count
    global error_count
    
    USER_AGENT = user_agent_rotator.get_random_user_agent()
    url = 'https://telegram.org/abuse'
    try:
        # Step 1: Send initial request and store cookies
        response = requests.get(url, proxies={'http': f'{proxy_type}://{proxy}', 'https': f'{proxy_type}://{proxy}'}, timeout=time_out)
    except AttributeError:
        error_count += 1
        pass
    except Exception as e:
        error_count += 1
        return errors.write(f'{e}\n')
        
    cookies = response.cookies

    # Step 2: Parse the HTML for the form
    soup = BeautifulSoup(response.text, 'html.parser')
    form = soup.find('form', action="/support")

    # Check if form is found
    if not form:
        print("Form not found on the page.")
        exit()

    # Step 3: Fill the form with data
    message_input = form.find('textarea', id='support_problem')
    email_input = form.find('input', id='support_email')
    phone_input = form.find('input', id='support_phone')

    # Fill the form with randomly selected data
    message = get_random_line('message.txt', username)
    email = generate('gmail')
    phone = generate_random_phone_number()

    if message_input:
        message_input['value'] = message
    if email_input:
        email_input['value'] = email
    if phone_input:
        phone_input['value'] = phone

    # Step 4: Prepare form data
    data = {input['name']: input.get('value', '') for input in form.find_all(['input', 'textarea'])}

    # Include hidden inputs
    hidden_inputs = form.find_all('input', type='hidden')
    for hidden_input in hidden_inputs:
        data[hidden_input['name']] = hidden_input['value']

    # Step 5: Send the POST request with stored cookies
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = requests.post(url, data=data, cookies=cookies, headers=headers)

    # Check the response status code
        if response.status_code == 200:
            print(f"Report Successful with Email: {email}, Phone Number: {phone} and Message: {message} using Proxy: {proxy, proxy_type}\n")
            success_count += 1
        else:
            error_count += 1
            pass
            
    except AttributeError:
        error_count += 1
        pass
    except requests.exceptions.RequestException:
        error_count += 1
        pass
    except Exception as e:
        error_count += 1
        return errors.write(f'{e}\n')
    
def get_views_from_saved_proxies(proxy_type, proxies, username):
    for proxy in proxies:
        control(proxy.strip(), proxy_type, username)

def start_view():

    while True:
            threads = []
            for proxy_type in PROXIES_TYPES:
                with open(f"{proxy_type}_proxies.txt", 'r') as file:
                    proxies = file.readlines()
                chunked_proxies = [proxies[i:i + 70] for i in range(0, len(proxies), 70)]
                for chunk in chunked_proxies:
                    thread = Thread(target=get_views_from_saved_proxies, args=(proxy_type, chunk, username))
                    threads.append(thread)
                    thread.start()
            for t in threads:
                t.join()

        
E = '\033[1;31m'
B = '\033[2;36m'
G = '\033[1;32m'
S = '\033[1;33m'

def check_views():

    global success_count
    global error_count
    
    while True:
        print(f'{G}[ TOTAL THREADS ]: {B}{active_count()} ⇝⇝⇝⇝ \n{G}[ SUCCESSFULL REPORT ]: {S}{success_count}\n{G}[ FAILED REPORT ]: {E}{error_count}\n')
        
        sleep(4)

username = input("Enter the username of Channel, Person or Group you want to report. You can also use link:: ")

Thread(target=start_view).start()
Thread(target=check_views).start()
