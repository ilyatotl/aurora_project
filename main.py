from typing import List
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
import os
import shutil

app = FastAPI()

file_names: List[str] = []

@app.get("/")
async def read_root():
    return {"Current files": file_names}


@app.post("/api/v1/upload/{name}")
async def upload_file(name: str, file: UploadFile):
    for file_name in file_names:
        if file_name == name:
            raise HTTPException(status_code=400, detail="This file name already exists")
    
    with open("files/" + name, "wb") as wf:
        shutil.copyfileobj(file.file, wf)

    file_names.append(name)
    return {name: "was added to the server"}
    

@app.get("/api/v1/download/{name}")
async def download_file(name: str):
    file_path = os.getcwd() + "/files/" + name
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type='application/octet-stream', filename=name)

    raise HTTPException(status_code=404, detail="No files with that name")
