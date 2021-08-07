from PIL import Image
import re
from io import BytesIO
import base64
from fastapi import HTTPException


class decode:
    def __init__(self, image):
        self.image = image

    def initial_validation(self):
        if self.image == "":
            raise HTTPException(
                status_code=400, detail="Image cannot be empty.")

    def remove_prefix(self):
        if(re.search('^data:image/png;base64,', self.image) == None):
            raise HTTPException(
                status_code=400, detail="base64 image data with prefix 'data:image/png;base64,' is needed to decode a message.")

        self.data = re.sub('^data:image/png;base64,', '',
                           self.image)

    def decode_from_base64(self):
        try:
            self.image_data = base64.b64decode(self.data)
        #  will raise error only if string is not base64. It doesn't know about image data.
        except Exception:
            raise HTTPException(
                status_code=400, detail="Invalid base64-encoded string.")

    def convert_to_rgb(self):
        try:
            with Image.open(BytesIO(self.image_data)) as self.im:
                self.im = self.im.convert("RGB")
        # occurs if base64 string was not image data
        except Exception:
            raise HTTPException(
                status_code=400, detail="base64 image data with prefix 'data:image/png;base64,' is needed to decode a message.")

    def get_2n_bits(self, number):
        result = ""
        try:
            for _ in range(0, number):
                result = result + \
                    bin(self.pixels[self.pixel_number[0],
                                    self.pixel_number[1]][self.pixel_number[2]])[2:].zfill(8)[6:8]
                # to get next r g or b value of the pixel.
                if (self.pixel_number[2] == 2):
                    if(self.pixel_number[0] < self.im.width-1):
                        self.pixel_number[0] = self.pixel_number[0] + 1
                    else:
                        self.pixel_number[0] = 0
                        self.pixel_number[1] = self.pixel_number[1] + 1
                    self.pixel_number[2] = 0
                else:
                    self.pixel_number[2] = self.pixel_number[2] + 1
            return result
        except:
            # expecting only index out of range errors.
            # will raise if requested more bits than there are availiable.
            # may happen only if can't find "10" in place of new character to break the loop.
            raise HTTPException(
                status_code=400, detail="Input image doesn't appear to have any encoded message.")

    def get_binary_data(self):
        try:
            self.pixels = self.im.load()
        except:
            raise HTTPException(
                status_code=500, detail="Unknown error while loading image.")

        self.pixel_number = [0, 0, 0]
        self.binary_data = []
        while True:
            current_chr = self.get_2n_bits(1)
            # 1 bit
            if (current_chr[0] == "0"):
                self.binary_data.append(current_chr + self.get_2n_bits(3))
            else:
                # end
                if (current_chr == "10"):
                    break
                else:
                    current_chr = current_chr + self.get_2n_bits(1)
                    # 2 bit
                    if(current_chr[0:3] == "110"):
                        append_this = current_chr[3:] + self.get_2n_bits(2)
                        if self.get_2n_bits(1) != "10":
                            raise HTTPException(
                                status_code=400, detail="Input image doesn't appear to have any encoded message.")
                        append_this = append_this + self.get_2n_bits(3)
                        self.binary_data.append(append_this)
                    # 3 bit
                    elif(current_chr == "1110"):
                        append_this = self.get_2n_bits(2)
                        if self.get_2n_bits(1) != "10":
                            raise HTTPException(
                                status_code=400, detail="Input image doesn't appear to have any encoded message.")
                        append_this = append_this + self.get_2n_bits(3)
                        if self.get_2n_bits(1) != "10":
                            raise HTTPException(
                                status_code=400, detail="Input image doesn't appear to have any encoded message.")
                        append_this = append_this + self.get_2n_bits(3)
                        self.binary_data.append(append_this)
                    else:
                        current_chr = current_chr + self.get_2n_bits(1)
                        # 4 bits
                        if(current_chr[0:5] == "11110"):
                            append_this = current_chr[5:] + self.get_2n_bits(1)
                            if self.get_2n_bits(1) != "10":
                                raise HTTPException(
                                    status_code=400, detail="Input image doesn't appear to have any encoded message.")
                            append_this = append_this + self.get_2n_bits(3)
                            if self.get_2n_bits(1) != "10":
                                raise HTTPException(
                                    status_code=400, detail="Input image doesn't appear to have any encoded message.")
                            append_this = append_this + self.get_2n_bits(3)
                            if self.get_2n_bits(1) != "10":
                                raise HTTPException(
                                    status_code=400, detail="Input image doesn't appear to have any encoded message.")
                            append_this = append_this + self.get_2n_bits(3)
                            self.binary_data.append(append_this)
                        else:
                            raise HTTPException(
                                status_code=400, detail="Input image doesn't appear to have any encoded message.")

    def decode_message(self):
        try:
            return "".join([chr(int(x, 2)) for x in self.binary_data])
        except:
            raise HTTPException(
                status_code=400, detail="Input image doesn't appear to have any encoded message.")

    def run(self):
        try:
            self.initial_validation()
            self.remove_prefix()
            self.decode_from_base64()
            self.convert_to_rgb()
            self.get_binary_data()
            return {"message": self.decode_message()}
        except:
            raise
