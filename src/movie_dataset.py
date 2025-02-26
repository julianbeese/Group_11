import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import ast
from pathlib import Path

DATA_DIR = Path("data")
EXTRACTED_DIR = DATA_DIR


class MovieDataset:
    def __init__(self):
        """
        Loading the data
        """
        self._load_data()

    def _load_data(self):
        """Loading the dataset into a pandas DataFrame"""
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

            # Einlesen der character.metadata.tsv mit expliziten Spaltennamenzuweisungen
            # basierend auf der tatsächlichen Struktur der Datei
            expected_columns = [
                "wiki_character_id",
                "freebase_movie_id",
                "release_date",  # Die Spalte, die falsch interpretiert wurde
                "character_name",  # Verschobene Spalte
                "actor_dob",  # Verschobene Spalte
                "actor_gender",  # Verschobene Spalte
                "actor_height",  # Verschobene Spalte
                "actor_ethnicity",  # Verschobene Spalte
                "actor_name",  # Verschobene Spalte
                "actor_age_at_movie_release",  # Verschobene Spalte
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
            print(f"Printing unique actor_gender values: {self.character_metadata['actor_gender'].unique()}")

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

        actor_counts = self.character_metadata.groupby("freebase_movie_id")["wiki_character_id"].count()
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
