
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
    headers = {'Authorization': hashtoken(),}
    response = requests.get(url, headers=headers) 
    return response.text, response.status_code



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
    if not CURRENT_TOKEN:
        print("Авторизируйтесь")
        return

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


def view_history():
    global CURRENT_TOKEN
    if not CURRENT_TOKEN:
        print(" Авторизируйтесь ")
        return

    body = {}
    headers = {'Authorization': hashtoken(body)}

    response = requests.get("http://127.0.0.1:8000/history", headers=headers)
    if response.status_code == 200:
        history = response.json().get("history", [])
        if not history:
            print("Ваша история пуста.")
        else:
            print("\n--- ВАША ИСТОРИЯ ЗАПРОСОВ ---")
            for item in history:
                print(f"[{item['time']}] | {item['action']}: | Ввод: {item['input']} | Вывод: {item['output']} |")
            print("---------------------\n")
    else:
        print("Не удалось получить историю:", response.json())


def delete_all_history():
    global CURRENT_TOKEN
    if not CURRENT_TOKEN:
        print("Авторизируйтесь")
        return

    headers = {'Authorization': hashtoken({})}
    response = requests.delete("http://127.0.0.1:8000/history", headers=headers)
    if response.status_code == 200:
        print("Ваша история удалена.")
    else:
        print("Ошибка при удалении:", response.json())


def show_all_texts():
    global CURRENT_TOKEN
    if not CURRENT_TOKEN:
        print("Авторизируйтесь")
        return

    headers = {'Authorization': hashtoken({})}
    response = requests.get("http://127.0.0.1:8000/texts", headers=headers)
    
    if response.status_code == 200:
        texts = response.json().get("texts", [])
        if not texts:
            print("База текстов пуста.")
        else:
            print("\n--- ТЕКСТЫ В БАЗЕ ---")
            for t in texts:
                print(f"ID: {t['id']} | {t['content']}")
            print("--------------------\n")
    else:
        print("Ошибка получения данных")


def add_text():
    global CURRENT_TOKEN
    if not CURRENT_TOKEN:
        print("Авторизируйтесь")
        return

    msg = input("Введите текст для сохранения: ")
    
    body = {"text": msg}

    headers = {'Authorization': hashtoken(body)}
    response = requests.post("http://127.0.0.1:8000/texts", json=body, headers=headers)
    if response.status_code == 200:
        res = response.json()
        print(f"Текст сохранен под номером: {res['id']}")
    else:
        print("Ошибка:", response.json())


def delete_text():
    global CURRENT_TOKEN
    if not CURRENT_TOKEN:
        print("Авторизируйтесь")
        return
    show_all_texts() 
    
    tid = input("Введите ID для удаления: ")
    if not tid: return

    headers = {'Authorization': hashtoken({})}
    response = requests.delete(f"http://127.0.0.1:8000/texts/{tid}", headers=headers)
    
    if response.status_code == 200:
        print("Текст успешно удален.")
    else:
        print("Ошибка удаления")


while (True):
    try:
        print("Введите команду")
        print("1 - Авторизация")
        print("2 - Регистрация")
        print("3 - Шифр Атбаш")
        print("4 - Просмотр истории")
        print("5 - Очистить историю")
        print("6 - Сохранить текст в базу")
        print("7 - Показать все тексты")
        print("8 - Удалить текст")
        command = int(input("Введите команду:"))
        match command:
            case 1:
                auth_user()
            case 2:
                reg_user()
            case 3:
                shifratbash()
            case 4:
                view_history()
            case 5:
                delete_all_history()
            case 6:
                add_text()
            case 7:
                show_all_texts()
            case 8:
                delete_text()
            case _:
                break
    except ValueError:
        print("Неверно")