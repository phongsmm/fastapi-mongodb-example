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

class Mention_delete(BaseModel):

    location: Location
    text :str


    

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
    x = list(db.tags.find({},{'text':0,'_id':0,'id':0,'mentions.location':0,'mentions.text':0}))

    person = 0
    location = 0
    Organization = 0
    JobTitle = 0
    Facility = 0
    GeographicFeature = 0
    Product = 0
    Date = 0
    Time = 0
    Duration = 0
    Measure = 0
    Money = 0
    Ordinal = 0
    Number = 0
    Percent = 0
    Address = 0
    PhoneNumber = 0
    EmailAddress = 0
    URL = 0
    IPAddress = 0
    Hashtag = 0
    TwitterHandle = 0
    
    for i in x :
        for i in (i.get('mentions')) :
            if(i.get('type')=="Person") :
                person+=1
            elif(i.get('type')=="Location"):
                location+=1
            elif(i.get('type')=="Organization"):
                Organization+=1
            elif(i.get('type')=="JobTitle"):
                JobTitle+=1
            elif(i.get('type')=="Facility"):
                Facility+=1
            elif(i.get('type')=="GeographicFeature"):
                GeographicFeature+=1
            elif(i.get('type')=="Product"):
                Product+=1
            elif(i.get('type')=="Date"):
                Date+=1
            elif(i.get('type')=="Time"):
                Time+=1
            elif(i.get('type')=="Duration"):
                Duration+=1
            elif(i.get('type')=="Measure"):
                Measure+=1
            elif(i.get('type')=="Money"):
                Money+=1
            elif(i.get('type')=="Ordinal"):
                Ordinal+=1
            elif(i.get('type')=="Number"):
                Number+=1
            elif(i.get('type')=="Percent"):
                Percent+=1
            elif(i.get('type')=="Address"):
                Address+=1
            elif(i.get('type')=="PhoneNumber"):
                PhoneNumber+=1
            elif(i.get('type')=="EmailAddress"):
                EmailAddress+=1
            elif(i.get('type')=="URL"):
                URL+=1
            elif(i.get('type')=="IPAddress"):
                IPAddress+=1
            elif(i.get('type')=="Hashtag"):
                Hashtag+=1
            elif(i.get('type')=="TwitterHandle"):
                TwitterHandle+=1


    



    return {"Data":db.tags.find().count(),"Person":person,"Location":location,"Organization":Organization,
    "JobTitle":JobTitle , "Facility":Facility ,"GeographicFeature":GeographicFeature,"Product":Product,"Date":Date,
    "Time":Time,"Duration":Duration,"Measure":Measure,"Money":Money,"Ordinal":Ordinal,"Number":Number,"Percent":Percent,
    "Address":Address,"PhoneNumber":PhoneNumber,"EmailAddress":EmailAddress,"URL":URL,"IPAddress":IPAddress,"Hashtag":Hashtag,
    "TwitterHandle":TwitterHandle
    }

    
@app.put("/update/{url_id}")
async def update(url_id:int,req : Ner_update = Body(...)):
    if(db.tags.find({"id":url_id}).count()>0) :
        db.tags.update_one({"id":url_id},{"$set":dict(req)})
        return dict(req)
        
    else :
        return{"Alert":"ID NOT FOUND!"}


@app.delete("/unset/{url_id}/{begin}/{end}")
async def unset(url_id:int,begin:int,end:int):
    if(db.tags.find({"id":url_id}).count()>0):
        db.tags.update_one({"id":url_id},{'$pull':{"mentions":{"location.begin":begin,"location.end":end}}})
        return {"Success":"Tag Deleted"}
    else :
        return{"Alert":"ID NOT FOUND!"}


@app.delete("/delete/{url_id}")
async def delete(url_id:int):
    if(db.tags.find({"id":url_id}).count()>0):
        db.tags.delete_one({"id":url_id})
        return {"Success":"Data Deleted"}
    else :
        return{"Alert":"ID NOT FOUND!"}


@app.put("/settype/{url_id}/{begin}/{end}/{_type}")
async def settype(url_id:int,begin:int,end:int,_type:str):
    if(db.tags.find({"id":url_id}).count()>0):
        db.tags.update_one({"id":url_id,"mentions.location.begin":begin,"mentions.location.end":end},{'$set':{"mentions.$.type":_type}})
        return {"Update":"Change to "+_type}
    else :
        return{"Alert":"ID NOT FOUND!"}


