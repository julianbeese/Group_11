"""
Streamlit Movie Data Analysis Dashboard

This script creates an interactive web application using Streamlit to visualize movie dataset analytics.
It provides three main sections:
1. Most Common Movie Types visualization
2. Actor Count per Movie histogram
3. Actor Height Distribution analysis with filtering options

"""

import streamlit as st
import pandas as pd
import numpy as np
from src.movie_dataset import MovieDataset


def load_dataset():
    """
    Initialize the MovieDataset class and handle potential loading errors.

    Returns:
        MovieDataset: Initialized dataset object if successful

    Raises:
        Exception: Propagates any error during dataset loading to be caught by Streamlit
    """
    return MovieDataset()


# Initialising the class with error handling
try:
    dataset = load_dataset()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# Streamlit App UI
st.title("🎬 Movie Data Analysis")


# --- SECTION 1: Most Common Movie Types ---
def display_movie_types_section(dataset):
    """
    Display interactive section for analyzing most common movie genres.

    Args:
        dataset (MovieDataset): The initialized movie dataset object
    """
    st.header("📊 Most Common Movie Types")
    N = st.number_input(
        "Select the Number to Display",
        min_value=1,
        max_value=50,
        step=1,
        value=10
    )
    try:
        counting = dataset.movie_type(N)
        st.write("Top Genre Chart")
        st.bar_chart(counting.set_index("Genre")["Count"], width=700, height=400)
    except Exception as e:
        st.error(f"Error generating genre counts: {e}")


# --- SECTION 2: Actor Count Histogram ---
def display_actor_count_section(dataset):
    """
    Display histogram of actor counts per movie.

    Args:
        dataset (MovieDataset): The initialized movie dataset object
    """
    st.header("🎭 Number of Actors per Movie")
    df_actor_count = dataset.actor_count()
    st.bar_chart(df_actor_count.set_index("Number_of_Actors")["Movie_Count"], width=700, height=400)


# --- SECTION 3: Actor Height Distribution ---
def display_height_distribution_section(dataset):
    """
    Display interactive section for actor height distribution analysis.

    Args:
        dataset (MovieDataset): The initialized movie dataset object
    """
    st.header("📏 Actor Height Distribution")

    gender_options = ["All"] + dataset.character_metadata["actor_gender"].dropna().astype(str).unique().tolist()
    selected_gender = st.selectbox("Select gender:", gender_options)

    min_height = st.number_input("Minimum height (cm):", min_value=0, max_value=300, value=150)
    max_height = st.number_input("Maximum height (cm):", min_value=0, max_value=300, value=200)

    if st.button("Show Height Distribution"):
        df_actor_heights = dataset.actor_distributions(
            gender=selected_gender,
            min_height=min_height,
            max_height=max_height
        )

        st.write(f"Actor Height Distribution for {selected_gender} - {len(df_actor_heights)} records found")

        heights = pd.to_numeric(df_actor_heights["actor_height"], errors="coerce").dropna()

        if len(heights) > 0:
            num_bins = min(20, len(heights))
            hist, bins = np.histogram(heights, bins=num_bins)
            bin_centers = (bins[:-1] + bins[1:]) / 2
            hist_df = pd.DataFrame({
                'height_bin': bin_centers,
                'count': hist
            })
            st.bar_chart(hist_df.set_index('height_bin'), height=400)
        else:
            st.warning("No data available for the selected criteria.")


# Execute the sections
display_movie_types_section(dataset)
display_actor_count_section(dataset)
display_height_distribution_section(dataset)