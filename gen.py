import requests
import random
import string
import time
import re
from colorama import Fore, Style, init
import threading
import queue


init()


def generate_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


def print_gradient(text):
    length = len(text)
    for i, char in enumerate(text):
        ratio = i / length
        r = int(255 * (1 - ratio))
        g = int(255 * ratio)
        b = 0
        print(f"\033[38;2;{r};{g};{b}m{char}", end='')
    print(Style.RESET_ALL)


verification_queue = queue.Queue()


def generate_account():
    email = generate_random_string(10) + "@1secmail.com"
    password = generate_random_string(12)
    username = generate_random_string(8)

    data = {
        "email": email,
        "password": password,
        "password_confirmation": password,
        "username": username
    }

    headers = {
        "content-type": "application/json",
        "origin": "https://vmateai.com",
        "referer": "https://vmateai.com/",
        "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"
    }

    response = requests.post("https://api.vmate.ai/api/v1/register_by_email", headers=headers, json=data)

    if response.status_code == 200:
        print_gradient(f"[+]Generated account: {email}:{password}")
        
        
        with open("credentials.txt", "a") as file:
            file.write(f"{email}:{password}:\n")
        
        
        verification_queue.put((email, password))
    else:
        print("[!]Failed to generate email and password.")


def verify_account():
    while True:
        email, password = verification_queue.get()
        
        time.sleep(3)
        inbox_url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={email.split('@')[0]}&domain=1secmail.com"
        inbox_response = requests.get(inbox_url)
        messages = inbox_response.json()

        if messages:
            message_id = messages[0]['id']
            message_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={email.split('@')[0]}&domain=1secmail.com&id={message_id}"
            message_response = requests.get(message_url)
            message_content = message_response.json()
            
            token_match = re.search(r'https://vmate.ai/confirm-email\?token=([\w-]+\.[\w-]+\.[\w-]+)', message_content['body'])
            if token_match:
                token = token_match.group(1)
                
                verify_data = {
                    "token": token
                }
                
                verify_headers = {
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                    "Connection": "keep-alive",
                    "Content-Length": "187",
                    "Content-Type": "application/json",
                    "Host": "api.vmate.ai",
                    "Origin": "https://vmateai.com",
                    "Referer": "https://vmateai.com/",
                    "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "cross-site",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
                }
                
                verify_response = requests.post("https://api.vmate.ai/api/v1/email_verify", headers=verify_headers, json=verify_data)
                
                if verify_response.status_code == 200:
                    print_gradient(f"[+]Verified: {email}:{token}")
                    
                    
                    with open("credentials.txt", "r") as file:
                        lines = file.readlines()
                    with open("credentials.txt", "w") as file:
                        for line in lines:
                            if line.startswith(f"{email}:{password}:"):
                                file.write(f"{email}:{password}:{token}\n")
                            else:
                                file.write(line)
            else:
                print("Token not found in the email.")
        else:
            print("No messages found.")
        
        verification_queue.task_done()


threads = int(input("[?]how much threads ->"))
loops = int(input("[?]how much accounts too gen ->"))


for _ in range(threads):
    thread = threading.Thread(target=generate_account)
    thread.daemon = True
    thread.start()


for _ in range(threads):
    thread = threading.Thread(target=verify_account)
    thread.daemon = True
    thread.start()


for _ in range(loops):
    generate_account()


verification_queue.join()
