from typing import Union
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import json
import time
from os import listdir
from os.path import isfile, join 
import os
import random


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


@app.get("/")
def root_path():
    return {"Hello": "World", "code": 744, "names":[{"name": "ivan", "surname": "ivanov",}]}



@app.get("/items/{item_id}")
def item_read(item_id: int, q: Union[str, None] = 0, a: Union[str, None] = 0 ):
    sum = q +a
    return {"item_id": item_id, "q": q, "a": a, "sum": sum}


@app.post("/items/")
def create_item(item: Item):
   item.id = int(time.time())

   with open(f"items/item_{item.id}.json", "w") as f:
       json.dump(item.model_dump(), f)
   return item


@app.get("/items")
def all_times(request: Request):
    token = request.headers.get('Authorization')
    if token != 'xxx':
        raise HTTPException(status_code=401, detail= "Invalid token")
    json_files_names = [file for file in os.listdir("items/") if file.endswith(".json")]
    data = []
    for json_file_name in json_files_names:
        file_path = os.path.join("items/", json_file_name)
        with open(file_path, "r") as f:
            data.append(json.load(f))
    return data


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
def create_user(params: AuthUser):
    json_files_names = [file for file in os.listdir("users/") if file.endswith(".json")]
    for json_file_name in json_files_names:
        file_path = os.path.join("users/", json_file_name)
        with open(file_path, "r") as f:
            json_item = json.load(f)
            user = User(**json_item)
            if user.login == params.login and user.password == params.password:
                return {"Login": user.login, "Token": user.token}
    raise HTTPException(status_code=401, detail="Неправльный логин или пароль")
