import json

from concealed.decode import Decode
from concealed.encode import Encode


def encode(
        input_image_path: str,
        output_image_folder: str,
        output_image_file_name: str,
        message_to_hide: str,
        password: str = None,
) -> dict:
    try:
        result = Encode(input_image_path,
                        output_image_folder,
                        output_image_file_name,
                        message_to_hide,
                        password).run()
        return result
    except Exception:
        raise


def decode(
        input_image_path: str,
        password: str = None,
) -> str:
    try:
        result = Decode(input_image_path, password).run()
        return json.dumps(result)
    except Exception:
        raise
