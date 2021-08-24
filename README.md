# hidden-api

FastAPI application, meant to be used for encoding and decoding messages in images i.e. steganography.

Note: It is encouraged to not use plain text as messages. [Reference for Advanced Encryption Standard](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard).

## supported formats for encode

### input

Note: APNG or other animated image inputs will have unintended transformations in the encoded image.

- PNG
- JPEG

### output

Note: Output image will be in RGBA color mode only.

PNG
