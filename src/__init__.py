"""
This file handles the data downloading and unzipping if there is no data
"""

import os
import tarfile
import pandas as pd
import requests
from pathlib import Path

class MovieDataset:
    DATA_URL = "http://www.cs.cmu.edu/~ark/personas/data/MovieSummaries.tar.gz"
    DOWNLOAD_DIR = Path("data")
    DATA_FILE = DOWNLOAD_DIR / "MovieSummaries.tar.gz"
    EXTRACTED_DIR = DOWNLOAD_DIR / "MovieSummaries"

    def __init__(self):
        self._prepare_data()
        self._load_data()

    def _prepare_data(self):
        """Ensure the dataset is downloaded and extracted."""
        self.DOWNLOAD_DIR.mkdir(exist_ok=True)

        if not self.DATA_FILE.exists():
            print("Downloading dataset...")
            self._download_data()

        if not self.EXTRACTED_DIR.exists():
            print("Extracting dataset...")
            self._extract_data()

    def _download_data(self):
        """Download the dataset."""
        response = requests.get(self.DATA_URL, stream=True)
        with open(self.DATA_FILE, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)

    def _extract_data(self):
        """Extract the dataset."""
        with tarfile.open(self.DATA_FILE, "r:gz") as tar:
            tar.extractall(self.DOWNLOAD_DIR)

    def _load_data(self):
        # TODO: loading the data into pandas dataframes
        pass
