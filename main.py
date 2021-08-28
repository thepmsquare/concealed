from fastapi import FastAPI, Form, File, UploadFile
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from encode import encode as e
from decode import decode as d
import json


middleware = [Middleware(CORSMiddleware, allow_origins=[
                         '*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])]
app = FastAPI()

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


@app.post("/decode", response_class=Response)
async def decode(image: UploadFile = File(...)):
    try:
        contents = await image.read()
        result = d(contents, image.content_type).run()
        return Response(content=json.dumps(result),
                        media_type="application/json",
                        headers={
                            "Access-Control-Allow-Origin": "*"
        })
    except Exception as e:
        print(e)
        raise


@app.get("/")
async def root():
    return {"message": "hidden-api"}
app.add_middleware(middleware)
