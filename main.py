from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from encode import encode as e
from decode import decode as d


app = FastAPI()
origins = [
    "https://thepmsquare.github.io/",
    "http://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# POST request because browsers do not allow GET request with a body


@app.post("/encode", response_class=Response)
async def encode(message: str = Form(...), image: UploadFile = File(...)):
    try:
        contents = await image.read()
        result = e(contents, message, image.content_type).run()

        return Response(content=result["buffered"],
                        media_type='image/png',
                        headers={
                            "percentOfImageModified": result["percentOfImageModified"],
                            "noOfPixelsModified": result["noOfPixelsModified"],
                            "Access-Control-Expose-Headers": "percentOfImageModified, noOfPixelsModified"
        }
        )
    except:
        raise


@app.post("/decode")
async def decode(image: UploadFile = File(...)):
    try:
        contents = await image.read()
        result = d(contents, image.content_type).run()
        return result
    except:
        raise


@app.get("/")
async def root():
    return {"message": "hidden-api"}
