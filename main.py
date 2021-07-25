from fastapi import FastAPI
from encode import encode as e
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*']
)


@app.get("/encode")
async def encode(image, message):
    return {"image": image,
            "message": message}


@app.get("/")
async def root():
    return {"message": "Hello World!"}
