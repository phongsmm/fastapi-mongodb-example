from typing import Optional
from fastapi import FastAPI , Body
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
from pymongo import MongoClient
from pydantic import BaseModel , Field
from bson import ObjectId
from datetime import datetime
from asynchat import async_chat


class PyObjectId(ObjectId):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid objectid')
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string')


class Event(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id')
    Text: str
    Date: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

class Add_Event(BaseModel):
    Text: str
    Date: Optional[datetime] = datetime.now()

class Add_News(BaseModel):
    Text: str
    Img_url:str
    Date: Optional[datetime] = datetime.now()

class Users(BaseModel):
    Username:str
    Password:str

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=config('ORIGINS'),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_DETAILS = config('MONGO_DETAILS')
client = MongoClient(MONGO_DETAILS)
db = client['Wattheplela']

@app.get("/")
def home():
    return {"message": "ยินดีต้อนรับ"}

@app.get("/get/")
async def show():
    data =[]
    for i in db.Data.find():
        data.append(Event(**i))

    return {'results':data}

@app.post('/event')
async def add_event(event: Add_Event):
    ret = db.Data.insert_one(event.dict(by_alias=True))
    return {'Event': event}

@app.post('/news')
async def add_news(news:Add_News ):
    ret = db.Data.insert_one(news.dict(by_alias=True))
    return {'News':news}

@app.post('/checkAdmin')
async def check_admin(user:Users):
    username = []
    password = []
    for e,i in enumerate(db.Users.find()):
        username.append(i['Username'])
        password.append(i['Password'])
    if user.Username in username:
        if user.Password == password[username.index(user.Username)]:
            return {'Status':'Successful'}
        else:
            return {'Status':'Access Denied'}
    else :
        return {'Status':'Access Denied'}



