from xml.dom.minidom import Element
from fastapi import FastAPI, Query, Depends, HTTPException, status
from pydantic import BaseModel
from pymongo import MongoClient
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from schema import user_model, lati_model, place_model, record_model, Token, TokenData
import hardware_back

SECRET_KEY = "b7c75abf6353c7e27e57b00542bf6459bf1ae50b86778dab6f2a92233b4f8733"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

client = MongoClient('mongodb://localhost', 27017)

db = client["Project"]

Front_Record = db["Frontend_Record"]
user_collection = db["User"]
place_collection = db["place"]

app = FastAPI()

app.include_router(hardware_back.router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(fake_db, username: str, password: str):
    user = user_collection.find_one({"username":username},{"_id":0})
    if (user == None):
        return False
    if not verify_password(password, user["password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.get("/record/street/{place}")
def get_record_by_place(place: str):
    result = Front_Record.find({"place": place},{"_id" :0,"place":0})
    myre = []
    for r in result:
        myre.append(r)
    return myre

@app.get("/record/all_street")
def get_record_all_place():
    result = place_collection.find({},{"_id" :0})
    myre = []
    for r in result:
        myre.append(r)
    return myre

@app.post("/register")
def register_user(user_model : user_model):
    check = user_collection.find_one({"username":user_model.username},{"_id":0})
    if (check == None):
        user_model.password = get_password_hash(user_model.password)
        user_model = jsonable_encoder(user_model)
        user_collection.insert_one(user_model)
        return {
            "result" : "Register complete"
        }
    else :
        return {
            "result" : "Username already used"
        }

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_from_db = user_collection.find_one({"Username":form_data.username},{"_id":0})
    user = authenticate_user(user_from_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/device/register")
async def device_register(place_model: place_model ,token: str = Depends(oauth2_scheme)):
    check = place_collection.find_one({"place":place_model.place},{"_id":0})
    if (check == None):
        place_model = jsonable_encoder(place_model)
        place_collection.insert_one(place_model)
        return {
            "result" : "Register complete"
        }
    else: 
        return {
            "result" : "Place already exist"
        }

@app.put("/speed/change")
async def speed_change(place_model: place_model ,token: str = Depends(oauth2_scheme)):
    check = place_collection.find_one({"place":place_model.place},{"_id":0})
    if (check != None):
        q = {"place":place_model.place}
        new = {"$set" : {"speed_limit":place_model.speed_limit}}
        place_collection.update_one(q, new)
        return {
            "result" : "Speed update complete"
        }
    else: 
        return {
            "result" : "Place not found"
        }

@app.delete("/record/delete")
async def delete_record(record_model: record_model ,token: str = Depends(oauth2_scheme)):
    q = {"place":record_model.place,"LaneNo":record_model.LaneNo,"velocity":record_model.velocity,"time":record_model.time}
    Front_Record.delete_one(q)
    return {
        "result" : "Delete complete"
    }

@app.get("/get/speed/{place}")
def get_speed(place:str):
    check = place_collection.find_one({"place":place},{"_id":0,"latLng":0})
    return check

@app.put("/put/check/record")
async def put_record(record_model: record_model ,token: str = Depends(oauth2_scheme)):
    q = {"place":record_model.place,"LaneNo":record_model.LaneNo,"velocity":record_model.velocity,"time":record_model.time}
    new = {"$set" : {"tick":record_model.tick}}
    Front_Record.update_one(q,new)
    return {
        "result" : "done"
    }

@app.delete("/device/delete")
async def delete_device(place_model: place_model ,token: str = Depends(oauth2_scheme)):
    q = {"place":place_model.place}
    place_collection.delete_one(q)
    return {
        "result" : "Delete complete"
    }