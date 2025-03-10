"""
Test module for the MovieDataset class.

This module contains tests for the expanded MovieDataset functionality,
including tests for the releases and ages methods.
"""

import unittest
import pandas as pd
from src.movie_dataset import MovieDataset


class TestMovieDataset(unittest.TestCase):
    """Test cases for the MovieDataset class."""

    @classmethod
    def setUpClass(cls):
        """Set up test class by initializing the MovieDataset."""
        try:
            cls.movie_dataset = MovieDataset()
        except Exception as e:
            raise unittest.SkipTest(f"Could not initialize MovieDataset: {e}")

    def test_releases_all(self):
        """Test the releases method with no genre filter."""
        releases = self.movie_dataset.releases()

        # Check that the result is a DataFrame with expected columns
        self.assertIsInstance(releases, pd.DataFrame)
        self.assertIn("Year", releases.columns)
        self.assertIn("Movie_Count", releases.columns)

        # Check that the result is not empty
        self.assertGreater(len(releases), 0)

        # Check that years are in ascending order
        self.assertTrue((releases["Year"].diff()[1:] > 0).all())

    def test_releases_with_genre(self):
        """Test the releases method with a genre filter."""
        # Get a valid genre from the dataset
        top_genres = self.movie_dataset.get_top_genres(1)
        if not top_genres:
            self.skipTest("No genres available in the dataset")

        genre = top_genres[0]
        releases = self.movie_dataset.releases(genre=genre)

        # Check that the result is a DataFrame with expected columns
        self.assertIsInstance(releases, pd.DataFrame)
        self.assertIn("Year", releases.columns)
        self.assertIn("Movie_Count", releases.columns)

    def test_get_top_genres(self):
        """Test the get_top_genres method."""
        top_genres = self.movie_dataset.get_top_genres(5)

        # Check that the result is a list
        self.assertIsInstance(top_genres, list)

        # Check that the list has the expected number of genres
        self.assertLessEqual(len(top_genres), 5)

    def test_ages_year(self):
        """Test the ages method with year grouping."""
        birth_years = self.movie_dataset.ages(time_unit="Y")

        # Check that the result is a DataFrame with expected columns
        self.assertIsInstance(birth_years, pd.DataFrame)
        self.assertIn("Year", birth_years.columns)
        self.assertIn("Birth_Count", birth_years.columns)

        # Check that the result is not empty
        self.assertGreater(len(birth_years), 0)

    def test_ages_month(self):
        """Test the ages method with month grouping."""
        birth_months = self.movie_dataset.ages(time_unit="M")

        # Check that the result is a DataFrame with expected columns
        self.assertIsInstance(birth_months, pd.DataFrame)
        self.assertIn("Month", birth_months.columns)
        self.assertIn("Birth_Count", birth_months.columns)
        self.assertIn("Month_Name", birth_months.columns)

        # Check that the result is not empty
        self.assertGreater(len(birth_months), 0)

        # Check that all months are between 1 and 12
        self.assertTrue(birth_months["Month"].between(1, 12).all())

    def test_ages_invalid_time_unit(self):
        """Test the ages method with an invalid time unit."""
        birth_data = self.movie_dataset.ages(time_unit="INVALID")

        # Should default to year grouping
        self.assertIsInstance(birth_data, pd.DataFrame)
        self.assertIn("Year", birth_data.columns)
        self.assertIn("Birth_Count", birth_data.columns)


if __name__ == "__main__":
    unittest.main()
