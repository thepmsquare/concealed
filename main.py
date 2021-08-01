from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from encode import encode as e
from decode import decode as d
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


class Decode(BaseModel):
    image: str

# POST request because browsers do not allow GET request with a body


@app.post("/encode")
async def encode(encode: Encode):
    try:
        result = e(encode.image, encode.message).run()
        return result
    except:
        raise


@app.post("/decode")
async def decode(decode: Decode):
    result = d(decode.image).run()
    return {"message": result}


@app.get("/")
async def root():
    return {"message": "Hello World!"}
