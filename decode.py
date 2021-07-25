from PIL import Image
import re
from io import BytesIO
import base64


class decode:
    def __init__(self, image):
        self.image = image

    def remove_prefix(self):

        self.data = re.sub('^data:image/.+;base64,', '',
                           self.image)

    def decode_from_base64(self):
        self.image_data = base64.b64decode(self.data)

    def convert_to_rgb(self):
        with Image.open(BytesIO(self.image_data)) as self.im:
            self.im = self.im.convert("RGB")

    def extract_binary_from_image(self):
        print("here")
        pixels = self.im.load()
        self.binary = []
        for i in range(0, self.im.width):
            for j in range(0, self.im.height):
                self.binary.append(pixels[i, j][0])
                self.binary.append(pixels[i, j][1])
                self.binary.append(pixels[i, j][2])
        for i in range(len(self.binary)):
            self.binary[i] = bin(self.binary[i])[2:].zfill(8)[6:8]
        self.binary = "".join(self.binary)

    def decode_message(self):
        self.normal_message = ""
        copy_encoded_message = self.binary
        while (len(copy_encoded_message) != 0):
            # 1 byte
            if (copy_encoded_message[0] == "0"):
                n = copy_encoded_message[1:8]
                self.normal_message = self.normal_message + \
                    chr(int(n, 2))
                copy_encoded_message = copy_encoded_message[8:]
            # 2 bytes
            elif(copy_encoded_message[0:3] == "110"):
                n = copy_encoded_message[3:8]+copy_encoded_message[10:16]
                self.normal_message = self.normal_message + \
                    chr(int(n, 2))
                copy_encoded_message = copy_encoded_message[16:]
            # 3 bytes
            elif(copy_encoded_message[0:4] == "1110"):
                n = copy_encoded_message[4:8] + \
                    copy_encoded_message[10:16] + copy_encoded_message[18:24]
                self.normal_message = self.normal_message + \
                    chr(int(n, 2))
                copy_encoded_message = copy_encoded_message[24:]
            # 4 bytes
            elif(copy_encoded_message[0:5] == "11110"):
                n = copy_encoded_message[5:8] + \
                    copy_encoded_message[10:16] + \
                    copy_encoded_message[18:24] + copy_encoded_message[26:32]
                self.normal_message = self.normal_message + \
                    chr(int(n, 2))
                copy_encoded_message = copy_encoded_message[32:]
            else:
                break

    def run(self):
        self.remove_prefix()
        self.decode_from_base64()
        self.convert_to_rgb()
        self.extract_binary_from_image()
        self.decode_message()
        return self.normal_message
