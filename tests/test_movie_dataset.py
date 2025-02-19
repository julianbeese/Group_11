"""
A Test for testing the movie dataset file
"""

import pytest
from src.movie_dataset import MovieDataset
import pandas as pd

@pytest.fixture
def dataset():
    """Creating an instance of the MovieDataset class"""
    return MovieDataset()

def test_movie_type_valid(dataset):
    """Testing if the class returns a valid datatype"""
    df = dataset.movie_type(5)
    assert isinstance(df, pd.DataFrame)
    assert "Movie_Type" in df.columns
    assert "Count" in df.columns
    assert len(df) <= 5
    print("test_movie_type_valid was successfull")

def test_movie_type_invalid():
    """Testing if an value error is raised if a wrong type is injected"""
    dataset = MovieDataset()
    with pytest.raises(ValueError):
        dataset.movie_type("ten")

def test_actor_distributions_invalid_gender(dataset):
    """Testing if a value error is raised if the gender is not a string"""
    with pytest.raises(ValueError):
        dataset.actor_distributions(gender=123)

def test_actor_distributions_invalid_height(dataset):
    """Testing if a value error is raised if the height is not a string"""
    with pytest.raises(ValueError):
        dataset.actor_distributions(min_height="short", max_height=200)

    with pytest.raises(ValueError):
        dataset.actor_distributions(min_height=150, max_height="tall")

def test_actor_distributions_valid(dataset):
    """Testing if the actor_distribution is of a correct type"""
    df = dataset.actor_distributions(gender="All", min_height=150, max_height=200)
    assert isinstance(df, pd.DataFrame)
    assert "height" in df.columns
