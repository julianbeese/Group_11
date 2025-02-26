"""
Movie Dataset Analysis Module

This module provides a class `MovieDataset` for loading and analyzing movie metadata and character data.
It includes functionality to:
- Load movie and character metadata from TSV files
- Analyze movie genre frequencies
- Calculate actor counts per movie
- Analyze actor height distributions with optional visualization

The data is expected to be in the 'data' directory relative to the script location.
"""

import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import ast
from pathlib import Path

DATA_DIR = Path("data")
EXTRACTED_DIR = DATA_DIR


class MovieDataset:
    """
    A class to handle movie dataset loading and analysis.

    Attributes:
        movie_metadata (pd.DataFrame): DataFrame containing movie metadata
        character_metadata (pd.DataFrame): DataFrame containing character metadata
    """

    def __init__(self):
        """
        Initialize the MovieDataset by loading the data.
        """
        self._load_data()

    def _load_data(self):
        """
        Load movie and character metadata from TSV files into DataFrames.

        Handles potential file loading errors and prints diagnostic information.
        """
        try:
            self.movie_metadata = pd.read_csv(
                EXTRACTED_DIR / "movie.metadata.tsv",
                sep="\t",
                header=None,
                names=[
                    "movie_id",
                    "title",
                    "release_date",
                    "revenue",
                    "runtime",
                    "languages",
                    "countries",
                    "genres",
                ],
            )

            expected_columns = [
                "wiki_character_id",
                "freebase_movie_id",
                "release_date",
                "character_name",
                "actor_dob",
                "actor_gender",
                "actor_height",
                "actor_ethnicity",
                "actor_name",
                "actor_age_at_movie_release",
                "freebase_character_map_1",
                "freebase_character_map_2",
                "freebase_character_map_3",
            ]

            self.character_metadata = pd.read_csv(
                EXTRACTED_DIR / "character.metadata.tsv",
                sep="\t",
                header=None,
                names=expected_columns,
                low_memory=False
            )

            print("Datasets loaded successfully.")

        except FileNotFoundError as e:
            print(f"Error loading dataset: {e}")

    def movie_type(self, N=10):
        """
        Calculate the N most common movie genres and their counts.

        Args:
            N (int, optional): Number of top genres to return. Defaults to 10.

        Returns:
            pd.DataFrame: DataFrame with columns "Genre" and "Count" showing the N most
                         common genres and their frequencies.

        Raises:
            TypeError: If N is not an integer.
            ValueError: If N is negative.
        """
        cnt = Counter()

        if not isinstance(N, int):
            raise ValueError("N must be an integer.")

        for item in self.movie_metadata["genres"]:
            if pd.isna(item):
                continue

            if isinstance(item, dict):
                genre_dict = item
            else:
                try:
                    genre_dict = ast.literal_eval(item)
                except Exception as e:
                    print(f"Parsing Error {e}")
                    continue

            cnt.update(genre_dict.values())

        df = pd.DataFrame(list(cnt.items()), columns=["Genre", "Count"])
        return df.nlargest(N, "Count").reset_index(drop=True)

    def actor_count(self):
        """
        Calculate a histogram of number of actors per movie.

        Returns:
            pd.DataFrame: DataFrame with columns "Number_of_Actors" and "Movie_Count"
                         showing the distribution of actors across movies.
        """
        actor_counts = self.character_metadata.groupby("freebase_movie_id")["wiki_character_id"].count()
        df = actor_counts.value_counts().reset_index()
        df.columns = ["Number_of_Actors", "Movie_Count"]
        return df

    def actor_distributions(self, gender="All", min_height=0.0, max_height=300.0, plot=False):
        """
        Calculate and optionally plot the height distribution of actors.

        Args:
            gender (str): Gender to filter by ("All" or specific gender). Defaults to "All".
            min_height (float): Minimum height in cm (inclusive). Defaults to 0.0.
            max_height (float): Maximum height in cm (inclusive). Defaults to 300.0.
            plot (bool): Whether to generate a histogram plot. Defaults to False.

        Returns:
            pd.DataFrame: Filtered DataFrame containing actor height data.

        Raises:
            ValueError: If gender is not a string or height parameters are not numeric.
        """
        if not isinstance(gender, str):
            raise ValueError("Gender must be a string.")
        if not isinstance(min_height, (int, float)) or not isinstance(max_height, (int, float)):
            raise ValueError("Height values must be numerical.")

        df = self.character_metadata.copy()
        df["actor_height"] = pd.to_numeric(df["actor_height"], errors="coerce")
        df = df.dropna(subset=["actor_height"])
        df = df[(df["actor_height"] >= min_height) & (df["actor_height"] <= max_height)]

        if gender != "All":
            df = df[df["actor_gender"] == gender]

        if plot:
            plt.hist(df["actor_height"], bins=30, edgecolor="black")
            plt.xlabel("Height (cm)")
            plt.ylabel("Frequency")
            plt.title(f"Height Distribution for Gender: {gender}")
            plt.show()

        return df