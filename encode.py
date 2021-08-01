from PIL import Image
import re
from io import BytesIO
import base64
from fastapi import HTTPException


class encode:
    def __init__(self, image, message):
        self.image = image
        self.message = message

    def initial_validation(self):
        if self.message == "":
            raise HTTPException(
                status_code=400, detail="Message cannot be empty.")
        if self.image == "":
            raise HTTPException(
                status_code=400, detail="Image cannot be empty.")

    def remove_prefix(self):
        if(re.search('^data:image/.+;base64,', self.image) == None):
            raise HTTPException(
                status_code=400, detail="base64 image data with prefix 'data:image/{format};base64,' is needed to encode a message.")
        self.data = re.sub('^data:image/.+;base64,', '',
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
                status_code=400, detail="base64 image data with prefix 'data:image/{format};base64,' is needed to encode a message.")

    def convert_message_to_binary(self):
        self.encoded_message = ""
        utf8_style = ""
        try:
            for i in self.message:
                unicode_number = ord(i)
                unicode_number_in_binary = format(ord(i), "b")
                utf8_style = ""
                if(unicode_number < 128):
                    utf8_style = unicode_number_in_binary.zfill(8)

                elif(unicode_number < 2048):
                    unicode_number_in_binary = unicode_number_in_binary.zfill(
                        11)
                    utf8_style = "110" + \
                        unicode_number_in_binary[0:5] + \
                        "10" + unicode_number_in_binary[5:12]

                elif(unicode_number < 65536):
                    unicode_number_in_binary = unicode_number_in_binary.zfill(
                        16)
                    utf8_style = "1110" + unicode_number_in_binary[0:4] + "10" + \
                        unicode_number_in_binary[4:10] + \
                        "10" + unicode_number_in_binary[10:16]

                elif(unicode_number <= 1114111):
                    unicode_number_in_binary = unicode_number_in_binary.zfill(
                        21)
                    utf8_style = "11110" + unicode_number_in_binary[0:3] + "10" + unicode_number_in_binary[3: 9] + \
                        "10" + unicode_number_in_binary[9:15] + \
                        "10" + unicode_number_in_binary[15:21]

                else:
                    raise Exception()

                self.encoded_message = self.encoded_message + utf8_style
        except Exception:
            raise HTTPException(
                status_code=500, detail="Unknown error occured while processing the message text.")

    def put_message_in_image(self):
        try:
            pixels = self.im.load()
        except:
            raise HTTPException(
                status_code=500, detail="Unknown error while loading image.")

        final_encoded_message = self.encoded_message + "10"
        msg_length = len(final_encoded_message)
        self.max_length = self.im.width * self.im.height * 3 * 2
        if(msg_length > self.max_length):
            raise HTTPException(
                status_code=400, detail="Image with more pixels needed for encoding current message.")

        pixel_number = [0, 0]
        self.pixel_count = 0
        for i in range(0, msg_length, 6):
            rm = final_encoded_message[i: i+2]
            gm = final_encoded_message[i+2: i+4]
            bm = final_encoded_message[i+4: i+6]
            # rm will always be full.
            r = int(
                format(pixels[pixel_number[0], pixel_number[1]][0], '08b')[0:6]+rm, 2)

            if (gm != ""):
                g = int(
                    format(pixels[pixel_number[0], pixel_number[1]][1], '08b')[0:6]+gm, 2)
            else:
                g = pixels[pixel_number[0], pixel_number[1]][1]

            if (bm != ""):
                b = int(
                    format(pixels[pixel_number[0], pixel_number[1]][2], '08b')[0:6]+bm, 2)
            else:
                b = pixels[pixel_number[0], pixel_number[1]][2]

            self.pixel_count = self.pixel_count + 1
            pixels[pixel_number[0], pixel_number[1]] = (r, g, b)
            if(pixel_number[0] < self.im.width-1):
                pixel_number[0] = pixel_number[0] + 1
            else:
                pixel_number[0] = 0
                pixel_number[1] = pixel_number[1] + 1

    def convert_PIL_image_to_data64(self):
        buffered = BytesIO()
        self.im.save(buffered, format="png")
        l = len(str(base64.b64encode(buffered.getvalue())))
        return "data:image/png;base64,"+str(base64.b64encode(buffered.getvalue()))[2:l-1]

    def run(self):
        try:
            self.initial_validation()
            self.remove_prefix()
            self.decode_from_base64()
            self.convert_to_rgb()
            self.convert_message_to_binary()
            self.put_message_in_image()
            image = self.convert_PIL_image_to_data64()
            return({"image": image, "noOfPixelsModified": self.pixel_count, "percentOfImageModified": (self.pixel_count/(self.im.width*self.im.height))*100})
        except:
            raise
