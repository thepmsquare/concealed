from PIL import Image
import re
from io import BytesIO
import base64
from fastapi import HTTPException


class encode:
    def __init__(self, image, message):
        self.image = image
        self.message = message

    def remove_prefix(self):
        self.format = self.image[11:self.image.index(";")]
        self.data = re.sub('^data:image/.+;base64,', '',
                           self.image)

    def decode_from_base64(self):
        self.image_data = base64.b64decode(self.data)

    def convert_to_rgb(self):
        with Image.open(BytesIO(self.image_data)) as self.im:
            self.im = self.im.convert("RGB")

    def convert_message_to_binary(self):
        self.encoded_message = ""
        for i in self.message:
            unicode_number = ord(i)
            unicode_number_in_binary = format(ord(i), "b")
            utf8_style = ""
            if(unicode_number < 128):
                utf8_style = unicode_number_in_binary.zfill(8)

            elif(unicode_number < 2048):
                unicode_number_in_binary = unicode_number_in_binary.zfill(11)
                utf8_style = "110" + \
                    unicode_number_in_binary[0:5] + \
                    "10" + unicode_number_in_binary[5:12]

            elif(unicode_number < 65536):
                unicode_number_in_binary = unicode_number_in_binary.zfill(16)
                utf8_style = "1110" + unicode_number_in_binary[0:4] + "10" + \
                    unicode_number_in_binary[4:10] + \
                    "10" + unicode_number_in_binary[10:16]

            elif(unicode_number <= 1114111):
                unicode_number_in_binary = unicode_number_in_binary.zfill(21)
                utf8_style = "11110" + unicode_number_in_binary[0:3] + "10" + unicode_number_in_binary[3: 9] + \
                    "10" + unicode_number_in_binary[9:15] + \
                    "10" + unicode_number_in_binary[15:21]
            self.encoded_message = self.encoded_message + utf8_style

    def put_message_in_image(self):
        pixels = self.im.load()
        copy_encoded_message = self.encoded_message+"10"
        msg_length = len(copy_encoded_message)
        max_length = self.im.width * self.im.height * 3 * 2
        if(msg_length > max_length):
            raise HTTPException(
                status_code=400, detail="Image with more pixels needed for encoding current message.")
        pixel_number = [0, 0]
        for i in range(0, msg_length, 6):
            rm = copy_encoded_message[i:i+2]
            gm = copy_encoded_message[i+2:i+4]
            bm = copy_encoded_message[i+4:i+6]

            r = int(
                format(pixels[pixel_number[0], pixel_number[1]][0], '08b')[0:6]+rm, 2)
            g = int(
                format(pixels[pixel_number[0], pixel_number[1]][0], '08b')[0:6]+gm, 2)
            b = int(
                format(pixels[pixel_number[0], pixel_number[1]][0], '08b')[0:6]+bm, 2)
            if(pixel_number[0] < self.im.width):
                pixel_number[0] = pixel_number[0] + 1
            else:
                pixel_number[0] = 0
                pixel_number[1] = pixel_number[1] + 1

    def convert_PIL_image_to_data64(self):
        buffered = BytesIO()
        self.im.save(buffered, format=self.format)
        l = len(str(base64.b64encode(buffered.getvalue())))
        return "data:image/"+self.format+";base64,"+str(base64.b64encode(buffered.getvalue()))[2:l-1]

    def run(self):
        try:
            self.remove_prefix()
            self.decode_from_base64()
            self.convert_to_rgb()
            self.convert_message_to_binary()
            self.put_message_in_image()

            return(self.convert_PIL_image_to_data64())
        except:
            raise
