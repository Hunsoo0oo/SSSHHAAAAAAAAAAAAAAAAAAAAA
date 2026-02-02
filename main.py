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

class User(BaseModel):
    login: str
    email: str
    password: str
    role: Union[str, None] = "basic role"
    token: Union[str, None] = None
    id: Union[int, None] = -1
    texts: list = [] #текста 
    history: list = [] #история че делал


class AuthUser(BaseModel):
    login: str
    password: str


class AtbashRequest(BaseModel):
    text: str


@app.post("/atbash")
async def atbash(request: Request):
    hashtoken = request.headers.get('Authorization')
    body = await request.json()

    result_session = session(hashtoken, body)
    if not result_session:
        raise HTTPException(status_code=401, detail="Неправльный данные")

    user_data, file_path = result_session
    text = str(body.get("text", ""))
    if not text:
        raise HTTPException(status_code=400, detail="Текст для шифрования не может быть пустым")
    text_to_process = text 
    target_text_obj = None
    is_id_input = False

    if text.isdigit():
        item_id = int(text)
        for t in user_data.get("texts", []):
            if int(t.get("id", 0)) == item_id:
                text_to_process = t["content"]
                target_text_obj = t
                is_id_input = True
                break

    rus_alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    eng_alphabet = "abcdefghijklmnopqrstuvwxyz"
    
    result_char = []
    for char in text_to_process:
        if char.lower() in rus_alphabet:
            alphabet = rus_alphabet
            minion = char.lower()
            oldi = alphabet.index(minion)
            newi = (len(alphabet) - 1) - oldi
            new_char = alphabet[newi]
            result_char.append(new_char if char.islower() else new_char.upper())
        elif char.lower() in eng_alphabet:
            alphabet = eng_alphabet
            minion = char.lower()
            oldi = alphabet.index(minion)
            newi = (len(alphabet) - 1) - oldi
            new_char = alphabet[newi]
            result_char.append(new_char if char.islower() else new_char.upper())
        else:
            result_char.append(char)
    
    final_result = ''.join(result_char)

    if is_id_input and target_text_obj:
        target_text_obj["content"] = final_result
        action_name = "atbash_update_by_id"
    else:
        if "texts" not in user_data:
            user_data["texts"] = []
        
        new_entry = {
            "id": int(time.time()),
            "content": final_result,
            "created_at": time.ctime()
        }
        user_data["texts"].append(new_entry)
        action_name = "atbash_encrypt_and_save"

    if "history" not in user_data:
        user_data["history"] = []
    user_data["history"].append({
        "action": "atbash_encryption",
        "input": text,
        "output": final_result,
        "time": time.ctime()
    })

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False)

    return {"result": final_result}


@app.get("/history")
async def get_history(request: Request):
    hashtoken = request.headers.get('Authorization')
    
    result_session = session(hashtoken, {}) 
    if not result_session:
        raise HTTPException(status_code=401, detail="Неправльный данные")
    user_data, file_path = result_session
    
    return {"history": user_data.get("history", [])}



@app.delete("/history")
async def clear_history(request: Request):
    hashtoken = request.headers.get('Authorization')
    
    result_session = session(hashtoken, {})
    if not result_session:
        raise HTTPException(status_code=401, detail="Неправльный данные")
    user_data, file_path = result_session
    
    user_data["history"] = []
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False)
        
    return True


@app.get("/texts")
async def get_all_texts(request: Request):
    hashtoken = request.headers.get('Authorization')
    result_session = session(hashtoken, {})
    if not result_session:
        raise HTTPException(status_code=401, detail="Неправльный данные")
    
    user_data, _ = result_session
    return {"texts": user_data.get("texts", [])}



@app.delete("/texts/{item_id}")
async def delete_text(item_id: int, request: Request):
    hashtoken = request.headers.get('Authorization')
    result_session = session(hashtoken, {})
    if not result_session:
        raise HTTPException(status_code=401)
    
    user_data, file_path = result_session
    old_texts = user_data.get("texts", [])
    
    new_texts = [t for t in old_texts if t["id"] != item_id]
    
    if len(old_texts) == len(new_texts):
        raise HTTPException(status_code=404, detail="Текст с таким ID не найден")

    user_data["texts"] = new_texts
    
    user_data["history"].append({
        "action": "delete_text",
        "input": f"ID: {item_id}",
        "output": "Успешно удалено",
        "time": time.ctime()
    })

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False)
        
    return True


@app.post("/texts")
async def add_text(request: Request):
    hashtoken = request.headers.get('Authorization')
    body = await request.json()
    
    result_session = session(hashtoken, body)
    if not result_session:
        raise HTTPException(status_code=401, detail="Неправльный данные")
    user_data, file_path = result_session
    
    new_text = body.get("text", "")
    if not new_text:
        raise HTTPException(status_code=400, detail="Сервер не смог обработать запрос из-за синтаксической ошибки или неправильного формата данных.")

    text = {
        "id": int(time.time()), 
        "content": new_text,
        "created_at": time.ctime()
    }

    if "texts" not in user_data:
        user_data["texts"] = []   
    user_data["texts"].append(text)
    if "history" not in user_data:
        user_data["history"] = []
        
    user_data["history"].append({
        "action": "add_text",
        "input": new_text,
        "output": f"ID {text['id']}",
        "time": time.ctime()
    })

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False)

    return {"id": text["id"]}


@app.patch("/texts/{item_id}")
async def update_text(item_id: int, request: Request):
    hashtoken = request.headers.get('Authorization')
    body = await request.json()
    
    result_session = session(hashtoken, body)
    if not result_session:
        raise HTTPException(status_code=401)
        
    user_data, file_path = result_session
    new_content = body.get("text", "")
    
    found = False
    for t in user_data.get("texts", []):
        if int(t["id"]) == item_id:
            t["content"] = new_content
            found = True
            break
            
    if not found:
        raise HTTPException(status_code=404, detail="Текст не найден")

    user_data["history"].append({
        "action": "edit_text",
        "input": f"ID: {item_id}",
        "output": f"New content: {new_content}",
        "time": time.ctime()
    })

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False)
    return True


@app.post("/users/")
def create_user(user: User):
   json_files_names = [file for file in os.listdir("users/") if file.endswith(".json")]
   for json_file_name in json_files_names:
        file_path = os.path.join("users/", json_file_name)
        with open(file_path, "r", encoding="utf-8") as f:
                openfiles = json.load(f)
                if openfiles.get("login") == user.login:
                    raise HTTPException(status_code=409, detail="Такой логин уже есть!")
   user.id = int(time.time())
   user.token = str(random.getrandbits(128))

   with open(f"users/user_{user.id}.json", "w", encoding="utf-8") as f:
       json.dump(user.model_dump(), f, ensure_ascii=False)
   return user


active_sessions = {}

@app.post("/users/auth")
def auth_user(params: AuthUser):
    json_files_names = [file for file in os.listdir("users/") if file.endswith(".json")]
    for json_file_name in json_files_names:
        file_path = os.path.join("users/", json_file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            json_item = json.load(f)
            user = User(**json_item)
            if user.login == params.login and user.password == params.password:
                ttoken = user.token
                session_seed = f"{user.token}{time.time()}"
                session_token = hashlib.sha256(session_seed.encode()).hexdigest()
                active_sessions[session_token] = user.login
                return {"Login": user.login, "Token": session_token, "TToken": ttoken }
    raise HTTPException(status_code=401, detail="Неправльный данные")


@app.patch("/users/password")
async def change_password(request: Request):
    hashtoken_val = request.headers.get('Authorization')
    body = await request.json()
    
    result_session = session(hashtoken_val, body)
    if not result_session:
        raise HTTPException(status_code=401)
        
    user_data, file_path = result_session
    user_data["password"] = body.get("new_password")
    user_data["token"] = str(random.getrandbits(128)) 

    user_data["history"].append({
        "action": "change_password",
        "input": "[********]",
        "output": "Succesfull",
        "time": time.ctime()
    })
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False)
    return True


def session(hashtoken: str, body: dict):
    tt = str(int(time.time()))
    for s_token, login in active_sessions.items():
        body_json = json.dumps(body, separators=(",", ":"), sort_keys=True)
        data = s_token + body_json + tt
        hashcheck = hashlib.sha256(data.encode('utf-8')).hexdigest()
        
        if hashcheck == hashtoken:
            json_files_names = [file for file in os.listdir("users/") if file.endswith(".json")]
            for json_file_name in json_files_names:
                file_path = os.path.join("users/", json_file_name)
                with open(file_path, "r", encoding="utf-8") as f:
                    json_item = json.load(f)
                    if json_item.get("login") == login:
                        return json_item, file_path
                        
    return None, None
