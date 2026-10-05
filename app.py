import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["ecse3038"]
devices = db["tutorial5"]

app = FastAPI()


class Device(BaseModel):
    name: str
    room: str
    temp: float
    online: bool


# Your handlers go below this line.

@app.get("/devices")    #task 1
def get_devices():
    return list(devices.find({}, {"_id": 0}))


@app.get("/devices/{name}")  #task 2: one device
def get_device(name: str):
    device = devices.find_one({"name": name}, {"_id": 0})
    if device is None:
        raise HTTPException(status_code=404, detail="No device called " + name)
    return device

@app.post("/devices", status_code=201)   #task 3: create device
def create_device(device: Device):
    if devices.find_one({"name": device.name}) is not None:
        raise HTTPException(status_code=409, detail="A device called " + device.name + " already exists")
    devices.insert_one(device.model_dump())
    return device.model_dump()


@app.put("/devices/{name}")     #task 4: update device
def put_device(name: str, device: Device, response: Response):
    new_device = device.model_dump()
    new_device["name"] = name
    result = devices.replace_one({"name": name}, new_device, upsert=True)
    if result.matched_count == 0:
        response.status_code = 201
    new_device.pop("_id", None)
    return new_device

@app.delete("/devices/{name}")  #task 5: delete device
def delete_device(name: str):
    result = devices.delete_one({"name": name})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No device called " + name)
    return {"deleted": name}