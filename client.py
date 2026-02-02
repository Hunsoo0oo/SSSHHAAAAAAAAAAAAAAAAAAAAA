
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
        ttoken = data.get("TToken")
        CURRENT_TOKEN = data["Token"]
        print("Авторизация прошла успешно")
        print(f"Сессионный токен: {data['Token']}")
        print(f"Технический токен {ttoken}")

    elif response.status_code == 401:
        print("Неверный логин или пароль")
    else:
        print(f" Ошибка {response.status_code}")


def update_password():
    global CURRENT_TOKEN
    print("--- СМЕНА ПАРОЛЯ ---")
    new_pass = pass_check()
    
    body = {"new_password": new_pass}
    headers = {'Authorization': hashtoken(body)}
    response = requests.patch("http://127.0.0.1:8000/users/password", json=body, headers=headers)
    
    if response.status_code == 200:
        print("Пароль изменен! Пожалуйста, авторизуйтесь заново.")
        CURRENT_TOKEN = None 
    else:
        print("Ошибка смены пароля")


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

    text = input("Введите текст для шифрования или ID: ")
    body = {"text": text}
    headers = {'Authorization': hashtoken(body)}


    response = requests.post("http://127.0.0.1:8000/atbash", json=body, headers=headers)
    code = response.status_code
    match code:
            case 200:
                final_result = response.json()["result"]
                print(f"Результат шифрования: {final_result}")
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


def edit_text():
    global CURRENT_TOKEN
    if not CURRENT_TOKEN:
        print("Авторизируйтесь")
        return
    show_all_texts()
    tid = input("Введите ID текста для редактирования: ")
    new_msg = input("Введите новый текст: ")
    
    body = {"text": new_msg}
    headers = {'Authorization': hashtoken(body)}
    response = requests.patch(f"http://127.0.0.1:8000/texts/{tid}", json=body, headers=headers)
    
    if response.status_code == 200:
        print("Текст успешно обновлен!")
    else:
        print("Ошибка обновления")



while (True):
    try:
        print("Введите команду")
        print("1 - Регистрация")
        print("2 - Авторизация")
        print("3 - Сменить пароль")
        print("4 - Шифр Атбаш")
        print("5 - Сохранить текст в базу")
        print("6 - Удалить текст")
        print("7 - Изменить текст")
        print("8 - Показать все тексты")
        print("9 - Просмотр истории")
        print("10 - Очистить историю")
        print("11 - Выход")
        command = int(input("Введите команду:"))
        match command:
            case 1:
                reg_user()
            case 2:
                auth_user()
            case 3:
                update_password()
            case 4:
                shifratbash()
            case 5:
                add_text()
            case 6:
                delete_text()
            case 7:
                edit_text()
            case 8:
                show_all_texts()
            case 9:
                view_history()
            case 10:
                delete_all_history()
            case 11:
                break
    except ValueError:
        print("Неверно")