import uvicorn
from decouple import config


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0",port=8000, reload=True)