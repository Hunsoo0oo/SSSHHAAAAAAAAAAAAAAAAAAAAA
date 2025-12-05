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

class Item(BaseModel):
    name: str
    description: Union[str, None] = "Описание..."
    price: float
    id: Union[int, None] = -1 

    def __str__(self):
        return f"{self.name}, {self.description} за {self.price} рублей"


def send_get(url):
    headers = {'Authorization': hashtoken()}
    response = requests.get(url, headers=headers) 
    return response.text, response.status_code

def hashtoken():
    global CURRENT_TOKEN
    if CURRENT_TOKEN is None:
        return ""
    sha256_hash = hashlib.new('sha256')
    sha256_hash.update(CURRENT_TOKEN.encode('utf-8'))
    return sha256_hash.hexdigest()

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
        print("Авторизация прошла успешно",CURRENT_TOKEN)
        print(f'SHA-256:',hashtoken())
    elif response.status_code == 401:
        print("Неверный логин или пароль")
    else:
        print(f" Ошибка {response.status_code}")

    

def all_items():
    result, code = send_get("http://localhost:8000/items")
    match code:
        case 200:
            json_items = json.loads(result)
            for json_item in json_items:
                item =  Item(**json_item)
                if (item.description != None):
                    print(item)
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

    


while (True):
    try:
        print("Введите команду")
        command = int(input("1 - cписок товаров\n2 - добавить товар\n3 - регистрация\n4 - авторизация\n"))
        match command:
            case 1:
                all_items()
            case 2:
                create_item()
            case 3:
                reg_user()
            case 4:
                auth_user()
            case _:
                break
    except ValueError:
        print("Неверно")