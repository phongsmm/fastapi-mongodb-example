from typing import Optional
from fastapi import FastAPI , Body
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
from pymongo import MongoClient
from pydantic import BaseModel , Field
from bson import ObjectId
from datetime import datetime




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
    return {"message": "ยินดีต้อนรับเข้าสู่ API ของวัดเทพลีลา"}

@app.get("/get/")
async def show():
    data =[]
    for i in db.Data.find():
        data.append(Event(**i))

    return {'results':data}

@app.post('/event')
async def add_event(event: Add_Event):
    ret = db.Data.insert_one(event.dict(by_alias=True))
    return {'user': event}

