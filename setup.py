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
    description="python util module to provide encryption and decryption using steganography using the least significant bits of the RGB values of an image on top of advanced encryption standard.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/thepmsquare/concealed",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
)
