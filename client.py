import requests
import json
from pydantic import BaseModel
from typing import Union
#from os.path import json
import time
import random


class Item(BaseModel):
    name: str
    description: Union[str, None] = "Описание..."
    price: float
    id: Union[int, None] = -1

    def __str__(self):
        return f"{self.name}, {self.description} за {self.price} рублей"


def send_get(url):
    headers = {'Authorization': 'xxx'}
    response = requests.get(url, headers=headers) 
    return response.text, response.status_code



def reg_user():
    email = input("Email:")
    login = input("Логин:")
    password = input("Пароль:")
    password_confirmation = input("Подтвердите пароль:")
    if password == password_confirmation:  
        user = {"login": login, "email": email, "password": password}
        response = requests.post("http://127.0.0.1:8000/users/", json=user)
        if response.status_code == 200:
            print("Пользователь зарегистрирован")
        else:
            print("Ошибка регистрации")
    else:
        print("Пароли не совпадают")


def auth_user():
    login = input("Введите логин:")
    password = input("Введите пароль:")
    user = {"login": login, "password": password}
    response = requests.post("http://127.0.0.1:8000/users/auth", json=user)
    if response.status_code == 200:
        data = response.json()
        Token = data["Token"]
        print("Авторизация прошла успешно")
    else:
        print("Неверный логин или пароль")

    

def all_items():
    result, code = send_get("http://localhost:8000/items")
    match code:
        case 200:
            json_items = json.loads(result)
            for json_item in json_items:
                item =  Item(**json_item)
                if (item.description != None):
                    print(item)
        case 401:
            print("Неверные авторизационные данные")
        case 403:
            print("Доступ ограничен")
        case _:
            print("Неизвестная ошибка")
    


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