"""
Data Downloader and Extractor for Movie Summaries Dataset
This module handles the downloading and extraction of the Movie Summaries dataset
from Carnegie Mellon University.
It checks for existing data, downloads the dataset if necessary,
and extracts it to a local directory.
The dataset is downloaded from: http://www.cs.cmu.edu/~ark/personas/data/MovieSummaries.tar.gz
and stored in a 'data' directory relative to this script.
"""
import os
import tarfile
from pathlib import Path
from typing import Iterator, BinaryIO, Optional, Union

import requests
from requests.models import Response

DATA_URL: str = "http://www.cs.cmu.edu/~ark/personas/data/MovieSummaries.tar.gz"
DATA_DIR: Path = Path("data")
DATA_FILE: Path = DATA_DIR / "MovieSummaries.tar.gz"
EXTRACTED_DIR: Path = DATA_DIR

def download_and_extract_data() -> None:
    """
    Check for existing data and manage download and extraction process.
    Creates the data directory if it doesn't exist, downloads the dataset if not present,
    and extracts it if the extracted files aren't already available.
    """
    DATA_DIR.mkdir(exist_ok=True)
    if not EXTRACTED_DIR.exists():
        if not DATA_FILE.exists():
            print("Downloading dataset...")
            download_data()
        print("Extracting dataset...")
        extract_data()

def download_data() -> None:
    """
    Download the Movie Summaries dataset from the specified URL.
    Uses streaming download to handle large files efficiently, saving to the DATA_FILE path.
    """
    response: Response = requests.get(DATA_URL, stream=True, timeout=60)
    with open(DATA_FILE, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                file.write(chunk)

def extract_data() -> None:
    """
    Extract the downloaded tar.gz file to the data directory.
    Opens the tar file in read mode and extracts all contents to DATA_DIR.
    """
    with tarfile.open(DATA_FILE, "r:gz") as tar:
        tar.extractall(str(DATA_DIR))

# Execute the download and extraction when this module is run directly
if __name__ == "__main__":
    download_and_extract_data()
