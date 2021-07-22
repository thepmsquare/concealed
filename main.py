from fastapi import FastAPI
from encode import encode as e
app = FastAPI()


@app.get("/encode")
async def encode():
    message = e("image", "good").printer()
    return {"message": message}


@app.get("/")
async def root():
    return {"message": "Hello World!"}
