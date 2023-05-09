# uvicorn main:app --reload

from typing import List
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from passlib.context import CryptContext
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta
import os
import shutil
import psycopg2

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_SECRET_KEY = "50b9cc07db6b0758759ddaeaae02d8f6cab82f5cf4199dfdc7280241f269e761"
ACCESS_TOKEN_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30 * 6

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


class User(BaseModel):
    id: int
    full_name: str
    username: str
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str


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

    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO applications (name, developer, version, short_description, long_description) VALUES (%s, %s, %s, %s, %s)",
                       (name, developer, version, short_desc, long_desc,))
        conn.commit()

    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM applications WHERE name = %s", (name,))
        id = cursor.fetchone()[0]
        conn.commit()

    with open("files/" + str(id) + ".rpm", "wb") as wf:
        shutil.copyfileobj(upload_file.file, wf)

    with open("images/" + str(id) + ".png", "wb") as wf:
        shutil.copyfileobj(image.file, wf)

    return {name: "was added to the server"}


@app.get("/download/file/{id}")
async def download_file(id: int):
    file_path = os.getcwd() + "/files/" + str(id) + ".rpm"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type='application/octet-stream', filename=str(id) + ".rpm")

    raise HTTPException(status_code=404, detail="No files with that name")


@app.get("/download/picture/{id}")
async def download_picture(id: int):
    file_path = os.getcwd() + "/images/" + str(id) + ".png"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type='application/octet-stream', filename=str(id) + ".png")

    raise HTTPException(status_code=404, detail="No files with that name")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username=(%s)",
                       (username,))
        user = cursor.fetchone()
        conn.commit()

    if user is None:
        return False
    if not verify_password(password, user[4]):
        return False

    return User(id=user[0], full_name=user[1], username=user[2], email=user[3])


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, ACCESS_TOKEN_SECRET_KEY, ACCESS_TOKEN_ALGORITHM)
    return encoded_jwt


async def get_user(token: str):
    payload = jwt.decode(token, ACCESS_TOKEN_SECRET_KEY,
                         algorithms=[ACCESS_TOKEN_ALGORITHM])
    username = payload.get("sub")

    if username is None:
        raise HTTPException(status_code=401, detail="Could not authenticate")

    with conn.cursor() as cursor:
        cursor.execute("SELECT (id, full_name, username, email, encrypted_password) FROM users WHERE username=(%s)",
                       (username,))
        user = cursor.fetchall()

    if user == []:
        return False

    return User(id=user[0], full_name=user[1], username=user[2], email=user[3])


@app.post("/register")
async def register(full_name: str, username: str, email: str, password: str):
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM users WHERE (username=(%s) OR email=(%s))",
                       (username, email,))
        u = cursor.fetchall()
    if u != []:
        raise HTTPException(
            status_code=400,
            detail="User with such email or username already exists",
        )

    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO users (full_name, username, email, encrypted_password) VALUES (%s, %s, %s, %s)",
                       (full_name, username, email, pwd_context.hash(password),))
        conn.commit()


@app.post("/authenticate", response_model=Token)
async def authenticate(username: str, password: str):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
