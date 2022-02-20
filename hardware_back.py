from sqlite3 import Timestamp
from xml.dom.minidom import Element
from fastapi import FastAPI, Query, HTTPException, APIRouter
from typing import Optional
from pydantic import BaseModel
from pymongo import MongoClient
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from schema import sensor, alarm, record_model
import time

client = MongoClient('mongodb://localhost', 27017)

db = client["Project"]

collection = db["Hardware_Sensors"]
collection2 = db["place"]
collection3 = db["sensor"]
collection4 = db["alarm"]
collection5 = db["Frontend_Record"]

router = APIRouter(
    prefix="/hard",
    tags=["hard"]
)

velo1 = -1
velo2 = -1

@router.put("/alarm/update/{place}/{alarm}/{time}")
def alarm(place : str,alarm : int,time : int):
    q = {"place" : place}
    new = {"$set" : {"alarm":alarm,"time":int(time)}}
    collection4.update_one(q, new)
    return "done"

@router.post("/record/post")
def post_rercord(place:str,LaneNo:int,velocity:float,time:float):
    time_int = int(time)
    velo_float = float(velocity)
    record_model1 = record_model(
        place = place,
        LaneNo = LaneNo,
        velocity = velo_float,
        time = time_int
    )
    record_model1 = jsonable_encoder(record_model1)
    collection5.insert_one(record_model1)
    return {
        "rusult" : "done"
    }

@router.post("/sensor/post")
def post(sensor : sensor):
    print(sensor.s)
    ss = collection3.find_one({"sensor_no":1},{"_id":0})
    p = collection2.find_one({"place":ss["place"]},{"_id":0})
    q = {"place" : ss["place"]}
    if (sensor.s == 1) :
        time1 = datetime.now().timestamp()
        new = {"$set" : {"time1":time1}}
        collection.update_one(q,new)
    if (sensor.s == 2) : 
        time2 = datetime.now().timestamp()
        new = {"$set" : {"time2":time2}}
        collection.update_one(q,new)
        time5 = collection.find_one({"place":ss["place"]},{"_id":0})
        velo1 = 1/(time5["time2"] - time5["time1"]) * 3.6
        new = {"$set" : {"velo1":velo1}}
        collection.update_one(q,new)
        velo = collection.find_one({"place":ss["place"]},{"_id":0})
        print(velo["velo1"])
        print(p["speed_limit"])
        if (velo["velo1"] > p["speed_limit"]) : 
            print(1)
            alarm(ss["place"],1,time5["time2"])
            post_rercord(ss["place"],1,velo["velo1"],time5["time2"])
            new = {"$set" : {"velo1":0}}
            collection.update_one(q,new)
    velo = collection.find_one({"place":ss["place"]},{"_id":0})
    time5 = collection.find_one({"place":ss["place"]},{"_id":0})
    if (sensor.s == 3 and velo["velo1"] != 0): 
        time3 = datetime.now().timestamp()
        new = {"$set" : {"time3":time3},}
        collection.update_one(q,new)
        velo = collection.find_one({"place":ss["place"]},{"_id":0})
        time5 = collection.find_one({"place":ss["place"]},{"_id":0})
        velo2 = 100/(time5["time3"] - time5["time2"]) * 3.6
        new = {"$set" : {"velo2":velo2}}
        collection.update_one(q,new)
        if (velo["velo2"] > p["speed_limit"]/2):
            alarm(ss["place"],1,time5["time3"])
            velo = collection.find_one({"place":ss["place"]},{"_id":0})
            post_rercord(ss["place"],1,velo["velo2"],time5["time3"])
            time.sleep(2)
            alarm(ss["place"],0,0)



@router.get("/alarm/get")
def get_alarm_hard():
    check = collection4.find_one({},{"_id":0,"alarm":1})
    return check["alarm"]
    