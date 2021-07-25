from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from encode import encode as e
from pydantic import BaseModel
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=["*"]
)


class Encode(BaseModel):
    message: str
    image: str

# POST request because browsers do not allow GET request with a body


@app.post("/encode")
async def encode(encode: Encode):
    return {"encode": encode.message}


@app.get("/")
async def root():
    return {"message": "Hello World!"}
