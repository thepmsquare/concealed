import os

from concealed import encode, decode

print(
    encode(
        input_image_path=os.getcwd() + os.sep + "images" + os.sep + "input.png",
        output_image_folder=os.getcwd() + os.sep + "images",
        output_image_file_name="output",
        message_to_hide="123",
        password="😊😂",
    )
)

# {'output_file_path': 'path', 'no_of_pixels_modified': '134', 'percent_of_image_modified': '0.011488340192043894'}

print(
    decode(
        input_image_path=os.getcwd() + os.sep + "images" + os.sep + "output.png",
        password="😊😂",
    )
)
# {"message": "123"}
print(os.getcwd())
