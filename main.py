import json

from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from encode import encode as e
from decode import decode as d


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
                            "noOfPixelsModified": result["noOfPixelsModified"], "Access-Control-Allow-Origin": "*",
                            "Access-Control-Expose-Headers": "percentOfImageModified, noOfPixelsModified, Access-Control-Allow-Origin"
        }
        )
    except:
        raise


@app.post("/decode", response_class=Response)
async def decode(image: UploadFile = File(...)):
    try:
        contents = await image.read()
        result = d(contents, image.content_type).run()
        return Response(content=json.dumps(result),
                        media_type="application/json",
                        headers={
                            "Access-Control-Allow-Origin": "*", "Access-Control-Expose-Headers": "Access-Control-Allow-Origin"
        })
    except Exception as e:
        print(e)
        raise


@app.get("/")
async def root():
    return {"message": "hidden-api"}
