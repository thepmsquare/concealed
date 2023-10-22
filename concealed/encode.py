import base64
import os
from io import BytesIO

from PIL import Image
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from concealed.configuration import cstr_message_appended_at_end, cstr_salt


class Encode:
    def __init__(
        self,
        input_image_path,
        output_image_folder,
        output_image_file_name,
        message_to_hide,
        password,
    ):
        self.input_image_path = input_image_path
        self.output_image_folder = output_image_folder
        self.output_image_file_name = output_image_file_name
        self.im = None
        self.encoded_message = None
        self.max_length = None
        self.pixel_count = None
        try:
            if password is not None:
                password_bytes = password.encode()
                salt = cstr_salt.encode()

                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(), iterations=100000, salt=salt, length=32
                )
                self.message_to_hide = (
                    Fernet(base64.urlsafe_b64encode(kdf.derive(password_bytes)))
                    .encrypt(message_to_hide.encode())
                    .decode()
                )
            else:
                self.message_to_hide = message_to_hide
        except Exception:
            raise

    @staticmethod
    def initial_validation(content_type):
        if not (
            content_type.lower() == "png"
            or content_type.lower() == "jpeg"
            or content_type.lower() == "webp"
        ):
            raise Exception(
                "Unsupported image format. Currently supported formats: image/jpeg, image/png, image/webp.",
            )

    def convert_to_rgb(self):
        try:
            with Image.open(self.input_image_path) as self.im:
                self.initial_validation(self.im.format)
                if self.im.mode == "RGBA":
                    self.im = self.im.convert("RGBA")
                else:
                    self.im = self.im.convert("RGB")
        except Exception:
            raise

    def convert_message_to_binary(self):
        self.encoded_message = ""

        try:
            for i in self.message_to_hide:
                unicode_number = ord(i)
                unicode_number_in_binary = format(ord(i), "b")
                if unicode_number < 128:
                    utf8_style = unicode_number_in_binary.zfill(8)

                elif unicode_number < 2048:
                    unicode_number_in_binary = unicode_number_in_binary.zfill(11)
                    utf8_style = (
                        "110"
                        + unicode_number_in_binary[0:5]
                        + "10"
                        + unicode_number_in_binary[5:12]
                    )

                elif unicode_number < 65536:
                    unicode_number_in_binary = unicode_number_in_binary.zfill(16)
                    utf8_style = (
                        "1110"
                        + unicode_number_in_binary[0:4]
                        + "10"
                        + unicode_number_in_binary[4:10]
                        + "10"
                        + unicode_number_in_binary[10:16]
                    )

                elif unicode_number <= 1114111:
                    unicode_number_in_binary = unicode_number_in_binary.zfill(21)
                    utf8_style = (
                        "11110"
                        + unicode_number_in_binary[0:3]
                        + "10"
                        + unicode_number_in_binary[3:9]
                        + "10"
                        + unicode_number_in_binary[9:15]
                        + "10"
                        + unicode_number_in_binary[15:21]
                    )

                else:
                    raise Exception("Unrecognized character in message_to_hide.")

                self.encoded_message = self.encoded_message + utf8_style
        except Exception:
            raise

    def put_message_in_image(self):
        try:
            pixels = self.im.load()
        except Exception:
            raise

        final_encoded_message = self.encoded_message + cstr_message_appended_at_end
        msg_length = len(final_encoded_message)
        self.max_length = self.im.width * self.im.height * 3 * 2
        if msg_length > self.max_length:
            raise Exception(
                "Image with more pixels needed for encoding current message_to_hide.",
            )

        pixel_number = [0, 0]
        self.pixel_count = 0
        for i in range(0, msg_length, 6):
            rm = final_encoded_message[i : i + 2]
            gm = final_encoded_message[i + 2 : i + 4]
            bm = final_encoded_message[i + 4 : i + 6]
            # rm will always be full.
            r = int(
                format(pixels[pixel_number[0], pixel_number[1]][0], "08b")[0:6] + rm, 2
            )

            if gm != "":
                g = int(
                    format(pixels[pixel_number[0], pixel_number[1]][1], "08b")[0:6]
                    + gm,
                    2,
                )
            else:
                g = pixels[pixel_number[0], pixel_number[1]][1]

            if bm != "":
                b = int(
                    format(pixels[pixel_number[0], pixel_number[1]][2], "08b")[0:6]
                    + bm,
                    2,
                )
            else:
                b = pixels[pixel_number[0], pixel_number[1]][2]
            self.pixel_count = self.pixel_count + 1
            if self.im.mode == "RGBA":
                a = pixels[pixel_number[0], pixel_number[1]][3]
                pixels[pixel_number[0], pixel_number[1]] = (r, g, b, a)
            else:
                pixels[pixel_number[0], pixel_number[1]] = (r, g, b)
            if pixel_number[0] < self.im.width - 1:
                pixel_number[0] = pixel_number[0] + 1
            else:
                pixel_number[0] = 0
                pixel_number[1] = pixel_number[1] + 1

    def convert_to_buffered(self):
        buffered = BytesIO()
        self.im.save(buffered, format="png")
        return buffered.getvalue()

    def run(self):
        try:
            self.convert_to_rgb()
            self.convert_message_to_binary()
            self.put_message_in_image()
            if not os.path.exists(self.output_image_folder):
                os.makedirs(self.output_image_folder)
            if self.output_image_folder[-1] == os.sep:
                output_file_path = (
                    self.output_image_folder + self.output_image_file_name + ".png"
                )
            else:
                output_file_path = (
                    self.output_image_folder
                    + os.sep
                    + self.output_image_file_name
                    + ".png"
                )
            self.im.save(output_file_path, format="PNG")

            return {
                "output_file_path": output_file_path,
                "no_of_pixels_modified": str(self.pixel_count),
                "percent_of_image_modified": str(
                    self.pixel_count / (self.im.width * self.im.height) * 100
                ),
            }

        except Exception:
            raise
