import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from pathlib import Path

DATA_DIR = Path("data")
EXTRACTED_DIR = DATA_DIR


class MovieDataset:
    def __init__(self):
        """
        loading the data
        """
        self._load_data()

    def _load_data(self):
        """loading the dataset into a pandas dataframe"""
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

            self.character_metadata = pd.read_csv(
                EXTRACTED_DIR / "character.metadata.tsv",
                sep="\t",
                header=None,
                names=["character_id", "movie_id", "actor_id", "gender", "height"],
            )

            print("Datasets loaded successfully.")

        except FileNotFoundError as e:
            print(f"Error loading dataset: {e}")

    def movie_type(self, N=10):
        """
        Calculates the N most common movie types and their counts.

        This method generates a Pandas DataFrame containing the N most frequent
        movie types found in the database, along with their respective counts.

        Parameters
        ----------
        N : int, default 10
            The number of most common movie types to retrieve.  Must be a non-negative integer.

        Returns
        -------
        pd.DataFrame
            A DataFrame with two columns: "Movie_Type" and "Count".
            "Movie_Type" contains the names of the N most common movie types,
            and "Count" contains the number of times each type appears in the database.
            Returns an empty DataFrame if no movie types are found.

        Raises
        ------
        TypeError
            If N is not an integer.
        ValueError
            If N is a negative integer.
        """
        if not isinstance(N, int):
            raise ValueError("N must be an integer.")

        genre_counts = Counter(
            genre.strip()
            for genres in self.movie_metadata["genres"].dropna()
            for genre in genres.split(",")
        )
        df = pd.DataFrame(
            genre_counts.items(), columns=["Movie_Type", "Count"]
        ).nlargest(N, "Count")
        return df

    def actor_count(self):
        """
        Calculates and returns a histogram of the number of actors per movie versus the number of movies with that actor count.

        This method analyzes the movie data to determine the distribution of actors across movies.
        It generates a Pandas DataFrame representing a histogram where the index represents the
        number of actors in a movie, and the 'Movie Count' column indicates the number of movies
        featuring that specific number of actors.

        Returns
        -------
        pd.DataFrame
            A DataFrame representing the actor count histogram. The index of the DataFrame
            corresponds to the number of actors in a movie, and the single column 'Movie Count'
            contains the number of movies with that many actors. Returns an empty DataFrame
            if no actor information is available.
        """

        actor_counts = self.character_metadata.groupby("movie_id")["actor_id"].count()
        df = actor_counts.value_counts().reset_index()
        df.columns = ["Number_of_Actors", "Movie_Count"]
        return df

    def actor_distributions(
        self, gender="All", min_height=0.0, max_height=300.0, plot=False
    ):
        """
        Calculates and optionally plots the height distribution of actors based on gender and height range.

        Parameters
        ----------
        gender : str
            The gender to filter by. Must be "All" to include all genders or a specific gender value present in the dataset.
        max_height : float
            The maximum height (inclusive) for filtering.
        min_height : float
            The minimum height (inclusive) for filtering.
        plot : bool, default False
            Whether to generate a matplotlib plot of the height distribution.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the height distribution.

        Raises
        ------
        ValueError
            If `gender` is not a string, or `min_height` or `max_height` are not numeric.
        """

        if not isinstance(gender, str):
            raise ValueError("Gender must be a string.")
        if not isinstance(min_height, (int, float)) or not isinstance(
            max_height, (int, float)
        ):
            raise ValueError("Height values must be numerical.")

        df = self.character_metadata.copy()

        df["height"] = pd.to_numeric(df["height"], errors="coerce")

        df = df.dropna(subset=["height"])

        df = df[(df["height"] >= min_height) & (df["height"] <= max_height)]

        if gender != "All":
            df = df[df["gender"] == gender]

        if plot:
            plt.hist(df["height"], bins=30, edgecolor="black")
            plt.xlabel("Height (cm)")
            plt.ylabel("Frequency")
            plt.title(f"Height Distribution for Gender: {gender}")
            plt.show()

        return df
