from pydantic import BaseModel
from typing import Optional

class user_model(BaseModel):
    username : str
    password : str

class lati_model(BaseModel):
    lat : float
    lng : float

class place_model(BaseModel):
    place : str
    latLng : Optional[lati_model] = None
    speed_limit : Optional[int] = 60

class record_model(BaseModel):
    place : str
    LaneNo : int
    velocity : int
    time : int

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class sensor(BaseModel):
    s : int

class alarm(BaseModel):
    lane : int
    place : str
    alarm : int
    time : int 