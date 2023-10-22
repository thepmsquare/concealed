from setuptools import setup, find_packages

setup(
    name="concealed",
    version="2.0.0",
    packages=find_packages(),
    package_data={
        "concealed": ["data/*"],
    },
    install_requires=["Pillow>=8.3.1", "cryptography>=41.0.4"],
    author="thePmSquare",
    author_email="thepmsquare@gmail.com",
    description="a python based utility, meant to be used for encoding and decoding messages in images i.e. steganography.",
    url="https://github.com/thepmsquare/concealed",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
)
