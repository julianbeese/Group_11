"""
Movie Dataset Analysis Module

This module provides a class `MovieDataset` for loading and analyzing movie metadata
and character data.
It includes functionality to:
- Load movie and character metadata from TSV files
- Analyze movie genre frequencies
- Calculate actor counts per movie
- Analyze actor height distributions with optional visualization
- Analyze movie releases by year and genre
- Analyze actor birth statistics by year or month
- Get random movies with their summaries and genres for LLM classification

The data is expected to be in the 'data' directory relative to the script location.
"""

import ast
from collections import Counter
import datetime
from pathlib import Path
import random

import pandas as pd
import matplotlib.pyplot as plt

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
                low_memory=False,
            )

            try:
                self.plot_summaries = pd.read_csv(
                    EXTRACTED_DIR / "plot_summaries.txt",
                    sep="\t",
                    header=None,
                    names=["movie_id", "summary"],
                    encoding="utf-8",
                )
            except FileNotFoundError:
                print(
                    "Plot summaries file not found. Some functionality will be limited."
                )
                self.plot_summaries = pd.DataFrame(columns=["movie_id", "summary"])

            print("Datasets loaded successfully.")

        except FileNotFoundError as e:
            print(f"Error loading dataset: {e}")

    def movie_type(self, n=10):
        """
        Calculate the n most common movie genres and their counts.

        Args:
            n (int, optional): Number of top genres to return. Defaults to 10.

        Returns:
            pd.DataFrame: DataFrame with columns "Genre" and "Count" showing the n most
                         common genres and their frequencies.

        Raises:
            TypeError: If n is not an integer.
            ValueError: If n is negative.
        """
        cnt = Counter()

        if not isinstance(n, int):
            raise ValueError("n must be an integer.")

        # Parse genres and count occurrences
        for item in self.movie_metadata["genres"]:
            if pd.isna(item):
                continue

            if isinstance(item, dict):
                genre_dict = item
            else:
                try:
                    genre_dict = ast.literal_eval(item)
                except (ValueError, SyntaxError) as e:
                    print(f"Parsing Error {e}")
                    continue

            cnt.update(genre_dict.values())

        df = pd.DataFrame(list(cnt.items()), columns=["Genre", "Count"])
        return df.nlargest(n, "Count").reset_index(drop=True)

    def actor_count(self):
        """
        Calculate a histogram of number of actors per movie.

        Returns:
            pd.DataFrame: DataFrame with columns "Number_of_Actors" and "Movie_Count"
                         showing the distribution of actors across movies.
        """
        actor_counts = self.character_metadata.groupby("freebase_movie_id")[
            "wiki_character_id"
        ].count()
        df = actor_counts.value_counts().reset_index()
        df.columns = ["Number_of_Actors", "Movie_Count"]
        return df

    def actor_distributions(
        self, gender="All", min_height=0.0, max_height=300.0, plot=False
    ):
        """
        Calculate and optionally plot the height distribution of actors.
        Handles height values stored in meters (e.g., 1.72) and converts to cm.

        Args:
            gender (str): Gender to filter by ("All" or specific gender). Defaults to "All".
            min_height (float): Minimum height in cm (inclusive). Defaults to 0.0.
            max_height (float): Maximum height in cm (inclusive). Defaults to 300.0.
            plot (bool): Whether to generate a histogram plot. Defaults to False.

        Returns:
            pd.DataFrame: Filtered DataFrame containing actor height data.
        """
        if not isinstance(gender, str):
            raise ValueError("Gender must be a string.")
        if not isinstance(min_height, (int, float)) or not isinstance(
            max_height, (int, float)
        ):
            raise ValueError("Height values must be numerical.")

        df = self.character_metadata.copy()
        df["actor_height"] = pd.to_numeric(df["actor_height"], errors="coerce")

        # Drop NaN values and convert height from meters to centimeters if necessary
        df = df.dropna(subset=["actor_height"])
        meter_mask = df["actor_height"] < 3.0
        df.loc[meter_mask, "actor_height"] = df.loc[meter_mask, "actor_height"] * 100
        df["actor_height"] = df["actor_height"].round(1)

        # Apply filters for height and gender
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

    def releases(self, genre=None):
        """
        Calculate the number of movies released per year, optionally filtered by genre.

        Args:
            genre (str, optional): Genre to filter by. If None, all movies are included.
                                   Defaults to None.

        Returns:
            pd.DataFrame: DataFrame with columns "Year" and "Movie_Count" showing the
                          number of movies released per year.
        """
        df = self.movie_metadata.copy()
        df["release_year"] = pd.to_numeric(
            df["release_date"].str.split("-").str[0], errors="coerce"
        )
        df = df.dropna(subset=["release_year"])
        df["release_year"] = df["release_year"].astype(int)

        if genre is not None:
            filtered_movies = []

            for idx, row in df.iterrows():
                if pd.isna(row["genres"]):
                    continue

                try:
                    if isinstance(row["genres"], dict):
                        genre_dict = row["genres"]
                    else:
                        genre_dict = ast.literal_eval(row["genres"])

                    if genre in genre_dict.values():
                        filtered_movies.append(idx)
                except (ValueError, SyntaxError):
                    continue

            df = df.loc[filtered_movies]

        year_counts = df["release_year"].value_counts().reset_index()
        year_counts.columns = ["Year", "Movie_Count"]

        year_counts = year_counts.sort_values("Year").reset_index(drop=True)

        return year_counts

    def get_top_genres(self, n=10):
        """
        Get the top n movie genres from the dataset.

        Args:
            n (int, optional): Number of top genres to return. Defaults to 10.

        Returns:
            list: List of the n most common genres.
        """
        genre_counts = self.movie_type(n)
        return genre_counts["Genre"].tolist()

    def ages(self, time_unit="Y"):
        """
        Calculate actor birth statistics by year or month.

        Args:
            time_unit (str, optional): Time unit for grouping births.
                                      "Y" for year, "M" for month. Defaults to "Y".

        Returns:
            pd.DataFrame: DataFrame with birth statistics according to the specified time unit.
        """
        df = self.character_metadata.copy()
        df = df.dropna(subset=["actor_dob"])

        if time_unit == "Y":
            df["birth_year"] = pd.to_datetime(df["actor_dob"], errors="coerce").dt.year

            df = df.dropna(subset=["birth_year"])

            birth_counts = df["birth_year"].value_counts().reset_index()
            birth_counts.columns = ["Year", "Birth_Count"]

            result = birth_counts.sort_values("Year").reset_index(drop=True)

        elif time_unit == "M":
            df["birth_month"] = pd.to_datetime(
                df["actor_dob"], errors="coerce"
            ).dt.month

            df = df.dropna(subset=["birth_month"])

            birth_counts = df["birth_month"].value_counts().reset_index()
            birth_counts.columns = ["Month", "Birth_Count"]

            result = birth_counts.sort_values("Month").reset_index(drop=True)

            month_names = {
                1: "January",
                2: "February",
                3: "March",
                4: "April",
                5: "May",
                6: "June",
                7: "July",
                8: "August",
                9: "September",
                10: "October",
                11: "November",
                12: "December",
            }
            result["Month_Name"] = result["Month"].map(month_names)

        else:
            print(f"Invalid time unit '{time_unit}'. Defaulting to Year.")
            return self.ages("Y")

        return result

    def get_random_movie(self):
        """
        Get a random movie with its genres, actors, and a generated summary based on title and genres.

        Returns:
            dict: Dictionary containing movie title, actors, genres, and a generated summary
                  or None if no suitable movie is found.
        """
        movie_df = self.movie_metadata.copy()

        movie_df = movie_df.dropna(subset=["genres"])

        if movie_df.empty:
            print("No movies found with genres")
            return None

        random_movie = movie_df.sample(1).iloc[0]
        movie_id = random_movie["movie_id"]
        movie_title = random_movie["title"]

        release_year = ""
        if not pd.isna(random_movie["release_date"]):
            try:
                release_year = random_movie["release_date"].split("-")[0]
            except (AttributeError, IndexError):
                pass

        genres_list = []
        try:
            if isinstance(random_movie["genres"], dict):
                genre_dict = random_movie["genres"]
            else:
                genre_dict = ast.literal_eval(random_movie["genres"])
            genres_list = list(genre_dict.values())
        except (ValueError, SyntaxError) as e:
            print(f"Error parsing genres: {e}")
            genres_list = []

        actors = []
        try:
            movie_characters = self.character_metadata[
                self.character_metadata["freebase_movie_id"] == movie_id
            ]

            movie_characters = movie_characters.sort_values("actor_name")

            actors = movie_characters["actor_name"].dropna().head(5).tolist()
        except Exception as e:
            print(f"Error finding actors: {e}")

        summary = self._generate_summary(movie_title, release_year, genres_list, actors)

        movie_info = {
            "title": movie_title,
            "summary": summary,
            "actors": actors,
            "genres": genres_list,
            "movie_id": movie_id,
            "release_year": release_year,
        }

        return movie_info

    def _generate_summary(self, title, year, genres, actors):
        """
        Generate a summary based on movie title, year, genres, and actors.

        Args:
            title (str): Movie title
            year (str): Release year
            genres (list): List of genres
            actors (list): List of actors

        Returns:
            str: Generated summary
        """
        genres_text = ", ".join(genres) if genres else "unknown genre"
        actors_text = ", ".join(actors) if actors else "unknown cast"
        year_text = f" ({year})" if year else ""

        summary = f"{title}{year_text} is a {genres_text} film"

        if actors:
            summary += f" starring {actors_text}"

        if "Comedy" in genres or "comedy" in [g.lower() for g in genres]:
            summary += ". The film features humorous situations and witty dialogue that entertain audiences."
        elif "Horror" in genres or "horror" in [g.lower() for g in genres]:
            summary += ". The movie creates an atmosphere of fear and suspense to thrill viewers."
        elif "Drama" in genres or "drama" in [g.lower() for g in genres]:
            summary += ". The story explores complex characters and emotional themes."
        elif "Action" in genres or "action" in [g.lower() for g in genres]:
            summary += (
                ". The film features exciting sequences with physical feats and stunts."
            )
        elif "Documentary" in genres or "documentary" in [g.lower() for g in genres]:
            summary += ". The film presents real-life events and issues through factual information."
        elif "Romance" in genres or "romance" in [g.lower() for g in genres]:
            summary += (
                ". The story focuses on the romantic relationships between characters."
            )
        elif "Thriller" in genres or "thriller" in [g.lower() for g in genres]:
            summary += ". The movie builds suspense and tension to keep viewers on the edge of their seats."
        elif (
            "Science Fiction" in genres
            or "sci-fi" in [g.lower() for g in genres]
            or "science fiction" in [g.lower() for g in genres]
        ):
            summary += ". The story explores futuristic concepts, advanced technology, or life in other worlds."
        else:
            summary += ". The film tells a compelling story that engages viewers from beginning to end."

        return summary

    def load_plot_summaries(self):
        """
        Return the plot summaries DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing movie_id and summary columns
        """
        if hasattr(self, "plot_summaries"):
            return self.plot_summaries
        else:
            try:
                self.plot_summaries = pd.read_csv(
                    EXTRACTED_DIR / "plot_summaries.txt",
                    sep="\t",
                    header=None,
                    names=["movie_id", "summary"],
                    encoding="utf-8",
                )
                return self.plot_summaries
            except FileNotFoundError:
                print("Plot summaries file not found.")
                return pd.DataFrame(columns=["movie_id", "summary"])
