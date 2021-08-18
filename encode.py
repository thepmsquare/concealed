from PIL import Image
import re
from io import BytesIO
from fastapi import HTTPException


class encode:
    def __init__(self, image, message, content_type):
        self.image = image
        self.message = message
        self.content_type = content_type

    def initial_validation(self):
        if(not(self.content_type == "image/png" or self.content_type == "image/jpeg")):
            raise HTTPException(
                status_code=400, detail="Unsupported image format. Currently supported formats: image/jpeg, image/png.")

    def convert_to_rgb(self):
        try:
            with Image.open(BytesIO(self.image)) as self.im:
                self.im = self.im.convert("RGB")
        except Exception as e:
            raise HTTPException(
                status_code=400, detail="Unable to convert image mode to RGB. " + str(e))

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
        except Exception as e:
            raise HTTPException(
                status_code=500, detail="Unexpected error while processing the message text. " + str(e))

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

    def convert_to_buffered(self):
        buffered = BytesIO()
        self.im.save(buffered, format="png")
        return buffered.getvalue()

    def run(self):
        try:
            self.initial_validation()
            self.convert_to_rgb()
            self.convert_message_to_binary()
            self.put_message_in_image()
            return(
                {
                    "buffered": self.convert_to_buffered(),
                    "noOfPixelsModified": str(self.pixel_count), "percentOfImageModified": str(
                        self.pixel_count/(self.im.width*self.im.height)*100
                    )
                }
            )

        except:
            raise
