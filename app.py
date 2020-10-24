from typing import Optional
from fastapi import FastAPI , Body
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
from pymongo import MongoClient
from pydantic import BaseModel
from bson import ObjectId





class Ner(BaseModel):
    id : int
    text : str
    mentions : list


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
db = client['Ner']

@app.get("/")
def home():
    return {"message": "Hello World"}

@app.get("/get/")
async def show():
    data =[]
    for tags in db.tags.find():
        data.append(Ner(**tags))

    return (data)


@app.post("/add/")
async def add(req : Ner = Body(...)):
    if(db.tags.find({"id":req.id}).count()>0):
        return {"Alert":"ID Exists"}
    db.tags.insert_one(dict(req))
    return dict(req);

@app.get("/list/")
async def all_list():
    person = db.tags.find({"mentions.type":"Person"}).count()
    location = db.tags.find({"mentions.type":"Location"}).count()
    number = db.tags.find({"mentions.type":"Number"}).count()

    return {"Person":person , "Location":location,"Number":number}

    
