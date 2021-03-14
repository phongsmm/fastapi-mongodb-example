from typing import Optional
from fastapi import FastAPI , Body , Depends , HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from decouple import config
from pymongo import MongoClient
from pydantic import BaseModel , Field
from bson import ObjectId
from datetime import datetime
from asynchat import async_chat
from passlib.hash import bcrypt
import jwt
import time

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
    Img_uri:str
    Detail:str
    Date: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

class Add_Event(BaseModel):
    Text: str
    Img_uri:str
    Detail:str
    Date: Optional[datetime] = datetime.now()

class Gallery(BaseModel):
    title:str
    Album:str
    Img_uri:str

class Picture(BaseModel):
    title:str

class Album(BaseModel):
    Album:str

class Add_News(BaseModel):
    Text: str
    Img_uri:str
    id:str
    Post_by:str
    Date: Optional[datetime] = datetime.now()

class Remove_News(BaseModel):
    id:str


class Users(BaseModel):
    Username: str
    Password: str
    
    @classmethod
    async def get_user(cls,username):
        return cls.get(username = username)
    

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=config('ORIGINS'),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_DETAILS = config('MONGO_DETAILS')
JWT_SECRET = config('JWT')
client = MongoClient(MONGO_DETAILS)
db = client['Wattheplela']



othen2_scheme = OAuth2PasswordBearer(tokenUrl='token')

@app.post('/token')
async def generate_token(from_data:OAuth2PasswordRequestForm = Depends()):
    user = authenticate(from_data.username , from_data.password)
    if not user:
        return {"Error":"Invalid Username or Password"}
    cur = db.Users.find_one({"Username":from_data.username})
    cur_dict = {"Username":cur['Username'],"Password":cur['Password'] , "exp":time.time()+500}
    token = jwt.encode(cur_dict,JWT_SECRET)
    return {"access_token":token , 'token_type':"bearer"}

@app.post('/get_token')
async def generate_token(user:Users):
    auth = authenticate(user.Username , user.Password)
    if not auth:
        return {"Error":"Invalid Username or Password"}
    cur = db.Users.find_one({"Username":user.Username})
    cur_dict = {"Username":cur['Username'],"Password":cur['Password'] , "exp":time.time()+500}
    token = jwt.encode(cur_dict,JWT_SECRET)
    return {"access_token":token , 'token_type':"bearer"}

async def get_current_user(token:str = Depends(othen2_scheme)):
    try:
        payload = jwt.decode(token,JWT_SECRET,algorithms=['HS256'])
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid Username or Password")
    return payload.get('Username')




@app.get("/")
def home():
    return {"message": "ยินดีต้อนรับ"}


@app.get("/event")
async def show():
    data =[]
    for i in db.Event.find():
        data.append(Event(**i))

    return {'results':data}

@app.get("/gallery")
async def gallery():
    data =[]
    for i in db.Gallery.find():
        data.append(Gallery(**i))

    return {'results':data}

@app.get("/news")
async def show():
    data =[]
    for i in db.News.find():
        data.append(Add_News(**i))

    return {'results':data}

@app.post('/news')
async def add_news(news:Add_News , user:str = Depends(get_current_user)):
    found = db.News.count_documents({"id":news.id})
    if found > 0:
        return {'Status':"ID Already Exist"}
    else:
        ret = db.News.insert_one({"Text":news.Text,"Img_uri":news.Img_uri,"id":news.id,"Post_by":user,"Date":news.Date})
        return {'Status':"Post Complete"}
    

@app.delete('/news')
async def remove_news(news:Remove_News , user:str = Depends(get_current_user)):
    try:

        ret = db.News.delete_one({})
        return {'results':news,'Status':'Deleted'}
    except Exception as e:
        return {'Status':e}
        




@app.post("/gallery")
async def add_to_gallery(img:Gallery, user:str = Depends(get_current_user)):
    ret = db.Gallery.insert_one(img.dict(by_alias=True))
    return {'Gallery': img}

@app.delete("/gallery")
async def add_to_gallery(img:Picture, user:str = Depends(get_current_user)):
    try:
        ret = db.Gallery.delete_one(img.dict(by_alias=True))
        return {'Status': "Delete Complete"}
    except Exception as e:
        return {'Error': e }


@app.delete("/album")
async def remove_album(img:Album, user:str = Depends(get_current_user)):
    try:
        ret = db.Gallery.delete_many(img.dict(by_alias=True))
        return {'Status': "Delete Complete"}
    except Exception as e:
        return {'Error': e }
    return {'Gallery': img}




@app.post('/event')
async def add_event(event: Add_Event , user:str = Depends(get_current_user)):
     ret = db.Event.insert_one({"Text":event.Text,"Detail":event.Detail,"Date":event.Date,"Img_uri":event.Img_uri,"Post_by":user})
     return {'Event': event , "Post_by":user}










@app.post('/register')
async def register(user: Users, admin:str = Depends(get_current_user)):
    ret = db.Users.insert_one({"Username":user.Username,"Password":bcrypt.hash(user.Password)})
    return {"result":{user.Username,bcrypt.hash(user.Password)}}


def verify(password,hashpassword):
    return bcrypt.verify(password,hashpassword)

def authenticate(username:str,password:str):
    found = db.Users.count_documents({"Username":username})
    cur = db.Users.find_one({"Username":username})
    
    if found < 1:
        return False
    if not verify(password , cur['Password']):
        return False
    return True




        

    

