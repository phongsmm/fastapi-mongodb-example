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


class Ner_update(BaseModel):
    text : str
    mentions : list

class Location(BaseModel) :
    begin : int
    end : int
class Mention_update(BaseModel):

    location: Location
    text :str
    type : str


    

class Type_update(BaseModel):

    type : str




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

    
@app.put("/update/{url_id}")
async def update(url_id:int,req : Ner_update = Body(...)):
    if(db.tags.find({"id":url_id}).count()>0) :
        db.tags.update_one({"id":url_id},{"$set":dict(req)})
        return dict(req)
        
    else :
        return{"Alert":"ID NOT FOUND!"}


@app.delete("/unset/{url_id}/")
async def unset(url_id:int,req: Mention_update = Body(...)):
    if(db.tags.find({"id":url_id}).count()>0):
        db.tags.update_one({"id":url_id},{"$pull":{"mentions":{'$in':[dict(req)]}}})
        return dict(req)
    else :
        return{"Alert":"ID NOT FOUND!"}


@app.put("/settype/{url_id}/{begin}/{end}")
async def settype(url_id:int,begin:int,end:int,req:Type_update = Body(...)):
    if(db.tags.find({"id":url_id}).count()>0):
        db.tags.update_one({"id":url_id,"mentions.location.begin":begin,"mentions.location.end":end},{'$set':{"mentions.$.type":dict(req)}})
        return dict(req)
    else :
        return{"Alert":"ID NOT FOUND!"}

