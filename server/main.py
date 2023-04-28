# uvicorn main:app --reload

from typing import List
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import os
import shutil
import psycopg2


conn = psycopg2.connect(dbname='aurora_store',
                        user='ilya', password='111111', host='172.17.0.1')

# host.docker.internal:host-gateway

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


def generate_file_name(name: str) -> str:
    return "_".join(name.split())


@app.get("/")
async def read_root():
    l: List[any] = []

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM applications")
        apps = cursor.fetchall()

        for app in apps:
            l.append({
                'id': app[0],
                'name': app[1],
                'developer': app[2],
                'version': app[3],
                'short_description': app[4],
                'long_description': app[5]})

    return JSONResponse(content=l, status_code=200)


@app.post("/upload/{name}")
async def upload_file(name: str, upload_file: UploadFile, image: UploadFile, developer: str, version: str, short_desc: str, long_desc: str):
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM applications WHERE name = %s', (name,))
        apps = cursor.fetchall()
        if apps != []:
            raise HTTPException(
                status_code=400, detail="This file name already exists")

    file_name = generate_file_name(name)

    with open("files/" + file_name + ".rpm", "wb") as wf:
        shutil.copyfileobj(upload_file.file, wf)

    with open("images/" + file_name + ".png", "wb") as wf:
        shutil.copyfileobj(image.file, wf)

    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO applications (name, developer, version, short_description, long_description) VALUES (%s, %s, %s, %s, %s)",
                       (name, developer, version, short_desc, long_desc,))
        conn.commit()

    return {name: "was added to the server"}


@app.get("/download/file/{name}")
async def download_file(name: str):
    file_name = generate_file_name(name)
    file_path = os.getcwd() + "/files/" + file_name + ".rpm"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type='application/octet-stream', filename=name + ".rpm")

    raise HTTPException(status_code=404, detail="No files with that name")


@app.get("/download/picture/{name}")
async def download_picture(name: str):
    file_name = generate_file_name(name)
    file_path = os.getcwd() + "/images/" + file_name + ".png"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type='application/octet-stream', filename=name + ".png")

    raise HTTPException(status_code=404, detail="No files with that name")


# @app.post("/register")
# async def register(email: str, password: str):
#     for e in users:
#         if e == email:
#             raise HTTPException(
#                 status_code=400, detail="User with this email already exists")

#     users[email] = password
#     return {email: "was registered"}


# @app.get("/authorize")
# async def authorize(email: str, password: str):
#     for e in users:
#         if e == email and users[e] == password:
#             return {email: "successfully authorized"}

#     raise HTTPException(status_code=401, detail="Wrong email or password")
