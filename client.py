from tkinter import CURRENT
import requests
import json
from pydantic import BaseModel
from typing import Union
#from os.path import json
import time
import random
import re
import hashlib
CURRENT_TOKEN = None



def send_get(url):
    headers = {'Authorization': hashtoken(),
               'Time': tt
               }
    response = requests.get(url, headers=headers) 
    return response.text, response.status_code


def hashtoken1():

    global CURRENT_TOKEN
    if CURRENT_TOKEN is None:
        return ""
    sha256_hash = hashlib.new('sha256')
    sha256_hash.update(CURRENT_TOKEN.encode('utf-8'))
    return sha256_hash.hexdigest()



def hashtoken2():
    global CURRENT_TOKEN
    if CURRENT_TOKEN is None:
        return ""
    tt = str(int(time.time()))
    sha256_hash = hashlib.new('sha256')
    sha256_hash.update((CURRENT_TOKEN + tt).encode('utf-8'))
    return sha256_hash.hexdigest()


def hashtoken3(body= None):
    global CURRENT_TOKEN
    if CURRENT_TOKEN is None:
        return ""
    body_json = json.dumps(body, separators=(",", ":"), sort_keys=True)
    tokenbody= CURRENT_TOKEN + body_json
    return hashlib.sha256(tokenbody.encode()).hexdigest()


def hashtoken(body= None):
    global CURRENT_TOKEN
    if CURRENT_TOKEN is None:
        return ""
    tt = str(int(time.time()))
    body_json = json.dumps(body, separators=(",", ":"), sort_keys=True)
    data = CURRENT_TOKEN + body_json + tt
    return hashlib.sha256(data.encode()).hexdigest()



def reg_user():
    email = input("Email:")
    login = input("Логин:")
    password = pass_check()
    user = {"login": login, "email": email, "password": password}
    response = requests.post("http://127.0.0.1:8000/users/", json=user)
    if response.status_code == 200:
        print("Пользователь зарегистрирован")
    elif response.status_code == 409:
        print("Логин уже занят")
    else:
        print("Ошибка регистрации")


def auth_user():
    global CURRENT_TOKEN
    login = input("Введите логин:")
    password = input("Введите пароль:")
    user = {"login": login, "password": password}
    response = requests.post("http://127.0.0.1:8000/users/auth", json=user)
    if response.status_code == 200:
        data = response.json()
        CURRENT_TOKEN = data["Token"]
        print("Авторизация прошла успешно")

    elif response.status_code == 401:
        print("Неверный логин или пароль")
    else:
        print(f" Ошибка {response.status_code}")



def pass_check():
    while (True):
        password = input("Пароль:")
        password_confirmation = input("Подтвердите пароль:")
    
        if password != password_confirmation: 
            print("Пароли не совпадают")
            continue

        if len(password) < 10:
            print("Пароль должен содержать не менее 10 символов")
            continue
    
        if not re.search(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#_])', password):
            print("Пароль должен содержать:")
            print("Cтрочные буквы (a–z)")
            print("Заглавные буквы (A–Z)")
            print("Цифры (0–9)")
            print("Спецсимволы: @$!%*?&#_")
            continue
    
        print("Пароль принят!")
        return password



def shifratbash():
    global CURRENT_TOKEN
    if CURRENT_TOKEN is None:
        return "Авторизируйтесь"

    text = input("Введите текст для шифрования Атбаш: ")
    body = {"text": text}
    headers = {'Authorization': hashtoken(body)}


    response = requests.post("http://127.0.0.1:8000/atbash", json=body, headers=headers)
    code = response.status_code
    match code:
            case 200:
                result = response.json()["result"]
                print(f"Результат шифрования: {result}")
            case 400:
                print("Сервер не смог обработать запрос из-за синтаксической ошибки или неправильного формата данных.")
            case 401:
                print("Неверные авторизационные данные")
            case 403:
                print("Доступ ограничен")
            case 404:
                print("Запрошенный ресурс не найден на сервере.")
            case 408:
                print("Сервер ожидал запрос, но получил его с задержкой.")
            case _:
                print("Неизвестная ошибка")


while (True):
    try:
        print("Введите команду")
        command = int(input("1 - авторизация\n2 - регистрация\n3 - Шифр Атбаш\n"))
        match command:
            case 1:
                auth_user()
            case 2:
                reg_user()
            case 3:
                shifratbash()
            case _:
                break
    except ValueError:
        print("Неверно")