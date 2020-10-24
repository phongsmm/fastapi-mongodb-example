from typing import Optional
from fastapi import FastAPI , Body
from fastapi.encoders import jsonable_encoder
from decouple import config
from pymongo import MongoClient
from pydantic import BaseModel
from bson import ObjectId



class Ner(BaseModel):
    id : int
    text : str
    mentions : list


app = FastAPI()
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

