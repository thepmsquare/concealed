from setuptools import setup, find_packages

setup(
    name="hidden_api",
    version="1.0.0",
    packages=find_packages(),
    package_data={
        "hidden_api": ["data/*"],
    },
    install_requires=[
        "fastapi==0.68.0",
        "Pillow==8.3.1",
        "python-multipart==0.0.5",
        "uvicorn==0.13.4",
        "square_logger~=1.0",
    ],
    author="thePmSquare",
    author_email="thepmsquare@thepmsquare.com",
    description="FastAPI application, meant to be used for encoding and decoding messages in images i.e. steganography.",
    url="https://github.com/thepmsquare/hidden-api",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
)
