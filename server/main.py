# uvicorn main:app --reload

from typing import List
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import os
import shutil
import psycopg2


def init_sql():
    with conn.cursor as cursor:
        cursor.execute(
            'CREATE TABLE applications (id PRIMARY KEY, name VARCHAR(64))')

        cursor.execute(
            'INSERT INTO applications (id, name) VALUES (1, image.bmp)')


conn = psycopg2.connect(dbname='aurora_store',
                        user='ilya', password='111111', host='localhost')

init_sql()

app = FastAPI()


class Application:
    def __init__(self,
                 name: str,
                 path: str,
                 picture_path: str,
                 short_description: str,
                 long_description: str):

        self.name = name
        self.path = path
        self.picture_path = picture_path
        self.short_description = short_description
        self.long_description = long_description


files: List[Application] = [Application(
    "Image", "files/image.bmp", "images/image.bmp", "short_description", "long_description")]
users = {}


@app.get("/")
async def read_root():
    file_names: List[str] = []

    for file in files:
        file_names.append(file.name)

    json_data = jsonable_encoder(file_names)
    return JSONResponse(content=json_data, status_code=200)


@app.post("/upload/{name}")
async def upload_file(name: str, upload_file: UploadFile, image: UploadFile, short_desc: str, long_desc: str):
    for file in files:
        if file.name == name:
            raise HTTPException(
                status_code=400, detail="This file name already exists")

    with open("files/" + name, "wb") as wf:
        shutil.copyfileobj(upload_file.file, wf)

    with open("images/" + name, "wb") as wf:
        shutil.copyfileobj(image.file, wf)

    files.append(Application(name, "files/" + name,
                 "images/" + name, short_desc, long_desc))

    return {name: "was added to the server"}


@app.get("/download/{name}")
async def download_file(name: str):
    file_path = os.getcwd() + "/files/" + name
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type='application/octet-stream', filename=name)

    raise HTTPException(status_code=404, detail="No files with that name")


@app.post("/register")
async def register(email: str, password: str):
    for e in users:
        if e == email:
            raise HTTPException(
                status_code=400, detail="User with this email already exists")

    users[email] = password
    return {email: "was registered"}


@app.get("/authorize")
async def authorize(email: str, password: str):
    for e in users:
        if e == email and users[e] == password:
            return {email: "successfully authorized"}

    raise HTTPException(status_code=401, detail="Wrong email or password")
