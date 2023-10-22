import json
from uuid import uuid4
from timeit import default_timer as timer

from fastapi import FastAPI, Form, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from uvicorn import run
from square_logger.main import SquareLogger

from hidden_api.configuration import (
    cbool_is_debug,
    cint_port,
    cstr_host_ip,
    cstr_log_file_name,
)
from hidden_api.encode import encode as e
from hidden_api.decode import decode as d


lobj_square_logger = SquareLogger(cstr_log_file_name)


def convert_bytes_to_human_readable(bytes_size):
    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
    base = 1024

    # Find the appropriate unit for the given bytes size
    unit_index = 0
    while bytes_size >= base and unit_index < len(units) - 1:
        bytes_size /= base
        unit_index += 1

    # Format the result with 2 decimal places
    formatted_size = "{:.2f}".format(bytes_size)
    unit = units[unit_index]

    return f"{formatted_size} {unit}"


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# POST request because browsers do not allow GET request with a body


@app.post("/encode", response_class=Response)
async def encode(
    request: Request, message: str = Form(...), image: UploadFile = File(...)
):
    req_uuid = ""
    try:
        start = timer()
        req_uuid = uuid4().__str__()
        contents = await image.read()
        lobj_square_logger.logger.info(
            f"Request for encode:\nuuid: {req_uuid}\nrequest.client.host: {request.client.host}\nimage size: {convert_bytes_to_human_readable(len(contents))}"
        )
        result = e(contents, message, image.content_type).run()
        end = timer()
        lobj_square_logger.logger.info(
            f"Response for encode:\nuuid: {req_uuid}\npercentOfImageModified: {result['percentOfImageModified']}\nnoOfPixelsModified: {result['noOfPixelsModified']}\ntime in seconds: {end - start}"
        )
        return Response(
            content=result["buffered"],
            media_type="image/png",
            headers={
                "percentOfImageModified": result["percentOfImageModified"],
                "noOfPixelsModified": result["noOfPixelsModified"],
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Expose-Headers": "percentOfImageModified, noOfPixelsModified, Access-Control-Allow-Origin",
            },
        )
    except Exception as ex:
        lobj_square_logger.logger.error(
            f"Exception in encode:\nuuid: {req_uuid}\nexception: {ex.detail}",
        )
        raise


@app.post("/decode", response_class=Response)
async def decode(request: Request, image: UploadFile = File(...)):
    req_uuid = ""
    try:
        start = timer()
        req_uuid = uuid4().__str__()
        contents = await image.read()
        lobj_square_logger.logger.info(
            f"Request for decode:\nuuid: {req_uuid}\nrequest.client.host: {request.client.host}\nimage size: {convert_bytes_to_human_readable(len(contents))}"
        )
        result = d(contents, image.content_type).run()
        end = timer()
        lobj_square_logger.logger.info(
            f"Response for decode:\nuuid: {req_uuid}\nlength of message: {len(result['message'])}\ntime in seconds: {end - start}"
        )
        return Response(
            content=json.dumps(result),
            media_type="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Expose-Headers": "Access-Control-Allow-Origin",
            },
        )
    except Exception as ex:
        lobj_square_logger.logger.error(
            f"Exception in decode:\nuuid: {req_uuid}\nexception: {ex.detail}",
        )
        raise


@app.get("/")
async def root(request: Request):
    lobj_square_logger.logger.info(
        f"Request for home:\nrequest.client.host: {request.client.host}"
    )
    return {"message": "hidden-api"}


if __name__ == "__main__":
    try:
        run(app, host=cstr_host_ip, port=cint_port, debug=cbool_is_debug)
    except Exception as exc:
        lobj_square_logger.logger.critical(exc, exc_info=True)
