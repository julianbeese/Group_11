"""
This file handles the data downloading and unzipping if there is no data
"""

import os
import tarfile
import requests
from pathlib import Path

DATA_URL = "http://www.cs.cmu.edu/~ark/personas/data/MovieSummaries.tar.gz"
DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "MovieSummaries.tar.gz"
EXTRACTED_DIR = DATA_DIR


def download_and_extract_data():
    """
    Checking if the data is already in the /data folder
    """
    DATA_DIR.mkdir(exist_ok=True)

    if not EXTRACTED_DIR.exists():
        if not DATA_FILE.exists():
            print("Downloading dataset...")
            download_data()

        print("Extracting dataset...")
        extract_data()


def download_data():
    """downloading the dataset"""
    response = requests.get(DATA_URL, stream=True)
    with open(DATA_FILE, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)


def extract_data():
    """extracting the data from the zip file"""
    with tarfile.open(DATA_FILE, "r:gz") as tar:
        tar.extractall(DATA_DIR)


download_and_extract_data()
