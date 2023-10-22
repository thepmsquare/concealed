import base64

from PIL import Image
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from concealed.configuration import cstr_message_appended_at_end, cstr_salt


class Decode:
    def __init__(self, input_image_path, password):
        self.input_image_path = input_image_path
        self.password = password
        self.im = None
        self.pixels = None
        self.pixel_number = None
        self.binary_data = None

    @staticmethod
    def initial_validation(content_type):
        if not (content_type.lower() == "png"):
            raise Exception(
                "Unsupported image format. Currently supported formats: image/png.",
            )

    def convert_to_rgb(self):
        try:
            with Image.open(self.input_image_path) as self.im:
                self.initial_validation(self.im.format)
                self.im = self.im.convert("RGB")
        except Exception:
            raise

    def get_2n_bits(self, number):
        result = ""
        try:
            for _ in range(0, number):
                result = (
                        result
                        + bin(self.pixels[self.pixel_number[0], self.pixel_number[1]][
                                  self.pixel_number[2]
                              ]
                              )[2:].zfill(8)[6:8]
                )
                # to get next r g or b value of the pixel.
                if self.pixel_number[2] == 2:
                    if self.pixel_number[0] < self.im.width - 1:
                        self.pixel_number[0] = self.pixel_number[0] + 1
                    else:
                        self.pixel_number[0] = 0
                        self.pixel_number[1] = self.pixel_number[1] + 1
                    self.pixel_number[2] = 0
                else:
                    self.pixel_number[2] = self.pixel_number[2] + 1
            return result
        except Exception:
            # expecting only index out of range errors.
            # will raise if requested more bits than there are available.
            # may happen only if it can't find "10" in place of new character to break the loop.
            raise Exception(
                "Input image doesn't appear to have any encoded message_to_hide.",
            )

    def get_binary_data(self):
        try:
            self.pixels = self.im.load()
        except Exception:
            raise

        self.pixel_number = [0, 0, 0]
        self.binary_data = []
        while True:
            current_chr = self.get_2n_bits(1)
            # 1 bit
            if current_chr[0] == "0":
                self.binary_data.append(current_chr + self.get_2n_bits(3))
            else:
                # end
                if current_chr == cstr_message_appended_at_end:
                    break
                else:
                    current_chr = current_chr + self.get_2n_bits(1)
                    # 2 bit
                    if current_chr[0:3] == "110":
                        append_this = current_chr[3:] + self.get_2n_bits(2)
                        if self.get_2n_bits(1) != "10":
                            raise Exception(
                                "Input image doesn't appear to have any encoded message_to_hide.",
                            )
                        append_this = append_this + self.get_2n_bits(3)
                        self.binary_data.append(append_this)
                    # 3 bit
                    elif current_chr == "1110":
                        append_this = self.get_2n_bits(2)
                        if self.get_2n_bits(1) != "10":
                            raise Exception(
                                "Input image doesn't appear to have any encoded message_to_hide.",
                            )
                        append_this = append_this + self.get_2n_bits(3)
                        if self.get_2n_bits(1) != "10":
                            raise Exception(
                                "Input image doesn't appear to have any encoded message_to_hide.",
                            )
                        append_this = append_this + self.get_2n_bits(3)
                        self.binary_data.append(append_this)
                    else:
                        current_chr = current_chr + self.get_2n_bits(1)
                        # 4 bits
                        if current_chr[0:5] == "11110":
                            append_this = current_chr[5:] + self.get_2n_bits(1)
                            if self.get_2n_bits(1) != "10":
                                raise Exception(
                                    "Input image doesn't appear to have any encoded message_to_hide.",
                                )
                            append_this = append_this + self.get_2n_bits(3)
                            if self.get_2n_bits(1) != "10":
                                raise Exception(
                                    "Input image doesn't appear to have any encoded message_to_hide.",
                                )
                            append_this = append_this + self.get_2n_bits(3)
                            if self.get_2n_bits(1) != "10":
                                raise Exception(
                                    "Input image doesn't appear to have any encoded message_to_hide.",
                                )
                            append_this = append_this + self.get_2n_bits(3)
                            self.binary_data.append(append_this)
                        else:
                            raise Exception(
                                "Input image doesn't appear to have any encoded message_to_hide.",
                            )

    def decode_message(self):
        try:
            return "".join([chr(int(x, 2)) for x in self.binary_data])
        except Exception:
            raise Exception(
                "Input image doesn't appear to have any encoded message_to_hide.",
            )

    def run(self):
        try:

            self.convert_to_rgb()
            self.get_binary_data()
            string_found_in_image = self.decode_message()
            if self.password is None:
                decoded_message = string_found_in_image
            else:
                password_bytes = self.password.encode()
                salt = cstr_salt.encode()

                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    iterations=100000,
                    salt=salt,
                    length=32
                )
                try:
                    decoded_message = Fernet(base64.urlsafe_b64encode(kdf.derive(password_bytes))).decrypt(
                        string_found_in_image.encode()).decode()
                except Exception:
                    raise Exception("Incorrect password.")
            return {"message": decoded_message}
        except Exception:
            raise
