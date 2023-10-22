# concealed

## about

python util module to provide encryption and decryption using steganography using the least significant bits of the RGB values of an image on top of advanced encryption standard. [reference for advanced encryption standard](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard).

## installation

> pip install concealed

## usage

[reference python file](./example.py)

## Supported formats

### input

- png
- jpeg
- webp

> note: apng or other animated image inputs will have unintended transformations in the encoded image.

### output

- png

> note: output image will be in rgb / rgba color modes only.

## configs

1. concealed\data\config.ini

## env

- python>=3.9.6

## changelog

### v2.0.0

- initial implementation as a python module.
- removed fastapi.
- validated webp support in input images.

### v1.0.0

- initial implementation using fastapi server.

## Feedback is appreciated. Thank you!
