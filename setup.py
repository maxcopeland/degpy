import setuptools

with open("README.md", "r") as rh:
    long_description = fh.read()

setuptools.setup(
    name="degpy-maxcopeland",
    version="0.0.1",
    author="Max Copeland",
    author_email="maxcopeland88@gmail.com",
    desciption=""" Package for interacting with degu ephys data at University of Montana's Insel Lab""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maxcopeland/degpy",
    packages=setuptools.find_packages,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)