from typing import Union
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import json
import time
from os import listdir
from os.path import isfile, join 
import os
import random
import hashlib

app = FastAPI()

class Item(BaseModel):
    name: str
    description: Union[str, None] = "Описание..."
    price: float
    id: Union[int, None] = -1


class User(BaseModel):
    login: str
    email: str
    password: str
    role: Union[str, None] = "basic role"
    token: Union[str, None] = None
    id: Union[int, None] = -1


class AuthUser(BaseModel):
    login: str
    password: str

class AtbashRequest(BaseModel):
    text: str


@app.get("/")
def root_path():
    return {"Hello": "World", "code": 744, "names":[{"name": "ivan", "surname": "ivanov"}]}


@app.post("/atbash")
async def atbash_endpoint(request: Request):
    hashtoken = request.headers.get('Authorization')
    body = await request.json()
    
    if not session(hashtoken, body):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    text = body.get("text", "")

    rus_alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    eng_alphabet = "abcdefghijklmnopqrstuvwxyz"
    
    result = []
    for char in text:
        if char.lower() in rus_alphabet:
            alphabet = rus_alphabet
            minion = char.lower()
            oldi = alphabet.index(minion)
            newi = (len(alphabet) - 1) - oldi
            new_char = alphabet[newi]
            result.append(new_char if char.islower() else new_char.upper())
        elif char.lower() in eng_alphabet:
            alphabet = eng_alphabet
            minion = char.lower()
            oldi = alphabet.index(minion)
            newi = (len(alphabet) - 1) - oldi
            new_char = alphabet[newi]
            result.append(new_char if char.islower() else new_char.upper())
        else:
            result.append(char)
    
    return {"result": ''.join(result)}


@app.post("/users/")
def create_user(user: User):
   json_files_names = [file for file in os.listdir("users/") if file.endswith(".json")]
   for json_file_name in json_files_names:
        file_path = os.path.join("users/", json_file_name)
        with open(file_path, "r") as f:
                openfiles = json.load(f)
                if openfiles.get("login") == user.login:
                    raise HTTPException(status_code=409, detail="Такой логин уже есть!")
   user.id = int(time.time())
   user.token = str(random.getrandbits(128))

   with open(f"users/user_{user.id}.json", "w") as f:
       json.dump(user.model_dump(), f)
   return user


@app.post("/users/auth")
def auth_user(params: AuthUser):
    json_files_names = [file for file in os.listdir("users/") if file.endswith(".json")]
    for json_file_name in json_files_names:
        file_path = os.path.join("users/", json_file_name)
        with open(file_path, "r") as f:
            json_item = json.load(f)
            user = User(**json_item)
            if user.login == params.login and user.password == params.password:
                return {"Login": user.login, "Token": user.token}
    raise HTTPException(status_code=401, detail="Неправльный логин или пароль")


def session(hashtoken: str,body: dict):
    json_files_names = [file for file in os.listdir("users/") if file.endswith(".json")]
    for json_file_name in json_files_names:
        file_path = os.path.join("users/", json_file_name)
        with open(file_path, "r") as f:
            json_item = json.load(f)
            token = json_item.get("token")
            if token:
                body_json = json.dumps(body, separators=(",", ":"), sort_keys=True)
                data = token + body_json
                hashcheck = hashlib.sha256(data.encode('utf-8')).hexdigest()
                if hashcheck == hashtoken:
                    return True
    return False

