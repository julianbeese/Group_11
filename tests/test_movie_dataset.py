"""
A Test for testing the movie dataset file

This test suite verifies the functionality of the MovieDataset class from src.movie_dataset.
It includes tests for:
- Valid movie type data return
- Invalid input handling for movie_type
- Invalid gender and height parameter handling for actor_distributions
- Valid actor distribution data return

"""

import pytest
from src.movie_dataset import MovieDataset
import pandas as pd

@pytest.fixture
def dataset():
    """
    Fixture to create an instance of MovieDataset for testing.

    Returns:
        MovieDataset: An initialized instance of the MovieDataset class
    """
    return MovieDataset()

def test_movie_type_valid(dataset):
    """
    Test that movie_type returns a valid DataFrame with expected structure.

    Args:
        dataset (MovieDataset): The MovieDataset instance from fixture

    Asserts:
        - Return type is pandas DataFrame
        - Required columns are present
        - Result length is within expected bounds
    """
    df = dataset.movie_type(5)
    assert isinstance(df, pd.DataFrame)
    assert "Genre" in df.columns
    assert "Count" in df.columns
    assert len(df) <= 5


def test_movie_type_invalid():
    """
    Test that movie_type raises ValueError for invalid input type.

    Verifies that passing a string instead of an integer raises the appropriate exception.
    """
    dataset = MovieDataset()
    with pytest.raises(ValueError):
        dataset.movie_type("ten")

def test_actor_distributions_invalid_gender(dataset):
    """
    Test that actor_distributions raises ValueError for non-string gender.

    Args:
        dataset (MovieDataset): The MovieDataset instance from fixture

    Verifies proper type checking for gender parameter.
    """
    with pytest.raises(ValueError):
        dataset.actor_distributions(gender=123)

def test_actor_distributions_invalid_height(dataset):
    """
    Test that actor_distributions raises ValueError for non-numeric height parameters.

    Args:
        dataset (MovieDataset): The MovieDataset instance from fixture

    Verifies proper type checking for min_height and max_height parameters.
    """
    with pytest.raises(ValueError):
        dataset.actor_distributions(min_height="short", max_height=200)

    with pytest.raises(ValueError):
        dataset.actor_distributions(min_height=150, max_height="tall")

def test_actor_distributions_valid(dataset):
    """
    Test that actor_distributions returns a valid DataFrame with expected structure.

    Args:
        dataset (MovieDataset): The MovieDataset instance from fixture

    Asserts:
        - Return type is pandas DataFrame
        - Required column 'height' is present
    """
    df = dataset.actor_distributions(gender="All", min_height=150, max_height=200)
    assert isinstance(df, pd.DataFrame)
    assert "actor_height" in df.columns