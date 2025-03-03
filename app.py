"""
Streamlit Movie Data Analysis Dashboard

This script creates an interactive web application using Streamlit to visualize
movie dataset analytics across multiple pages.

Pages:
1. Main Dashboard:
   - Most Common Movie Types visualization
   - Actor Count per Movie histogram
   - Actor Height Distribution analysis with filtering options

2. Chronological Analysis:
   - Movie releases per year (optionally filtered by genre)
   - Actor birth statistics by year or month
"""

import numpy as np
import pandas as pd
import streamlit as st

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


# Configure page settings
st.set_page_config(
    page_title="Movie Data Analysis",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initializing the class with error handling
try:
    movie_data = load_dataset()
except (FileNotFoundError, pd.errors.EmptyDataError, ValueError) as load_error:
    st.error(f"Error loading dataset: {load_error}")
    st.stop()


# Create navigation in sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Main Dashboard", "Chronological Analysis"])


# --- MAIN DASHBOARD PAGE ---
if page == "Main Dashboard":
    st.title("Movie Data Analysis - Main Dashboard")

    # --- SECTION 1: Most Common Movie Types ---
    def display_movie_types_section(movie_dataset):
        """
        Display interactive section for analyzing most common movie genres.

        Args:
            movie_dataset (MovieDataset): The initialized movie dataset object
        """
        st.header("Most Common Movie Types")
        num_genres = st.number_input(
            "Select the Number to Display", min_value=1, max_value=50, step=1, value=10
        )
        try:
            counting = movie_dataset.movie_type(num_genres)
            st.write("Top Genre Chart")
            st.bar_chart(counting.set_index("Genre")["Count"], width=700, height=400)
        except ValueError as genre_error:
            st.error(f"Error generating genre counts: {genre_error}")

    # --- SECTION 2: Actor Count Histogram ---
    def display_actor_count_section(movie_dataset):
        """
        Display histogram of actor counts per movie.

        Args:
            movie_dataset (MovieDataset): The initialized movie dataset object
        """
        st.header("Number of Actors per Movie")
        df_actor_count = movie_dataset.actor_count()
        st.bar_chart(
            df_actor_count.set_index("Number_of_Actors")["Movie_Count"],
            width=700,
            height=400,
        )

    # --- SECTION 3: Actor Height Distribution ---
    def display_height_distribution_section(movie_dataset):
        """
        Display interactive section for actor height distribution analysis.
        Handles heights stored in meters (e.g., 1.72).

        Args:
            movie_dataset (MovieDataset): The initialized movie dataset object
        """
        st.header("Actor Height Distribution")
        gender_options = ["All"] + movie_dataset.character_metadata[
            "actor_gender"
        ].dropna().astype(str).unique().tolist()
        selected_gender = st.selectbox("Select gender:", gender_options)

        # Update the min/max values to be more appropriate for heights in cm
        min_height = st.number_input(
            "Minimum height (cm):", min_value=0, max_value=300, value=150
        )
        max_height = st.number_input(
            "Maximum height (cm):", min_value=0, max_value=300, value=200
        )

        if st.button("Show Height Distribution"):
            df_actor_heights = movie_dataset.actor_distributions(
                gender=selected_gender, min_height=min_height, max_height=max_height
            )

            st.write(
                f"Actor Height Distribution for {selected_gender} - {len(df_actor_heights)} records found"
            )

            heights = df_actor_heights["actor_height"].values

            if len(heights) > 0:
                num_bins = min(30, len(heights))
                hist, bins = np.histogram(heights, bins=num_bins)
                bin_centers = (bins[:-1] + bins[1:]) / 2

                bin_centers = np.round(bin_centers, 1)

                hist_df = pd.DataFrame({"height_bin": bin_centers, "count": hist})

                st.bar_chart(hist_df.set_index("height_bin"), height=400)

                st.write("Height Statistics (cm):")
                st.write(f"Average: {heights.mean():.1f} cm")
                st.write(f"Minimum: {heights.min():.1f} cm")
                st.write(f"Maximum: {heights.max():.1f} cm")

            else:
                st.warning("No data available for the selected criteria.")

    display_movie_types_section(movie_data)
    display_actor_count_section(movie_data)
    display_height_distribution_section(movie_data)


# --- CHRONOLOGICAL ANALYSIS PAGE ---
elif page == "Chronological Analysis":
    st.title("Movie Data Analysis - Chronological Analysis")

    # --- SECTION 1: Movie Releases by Year ---
    st.header("Movie Releases by Year")

    top_genres = movie_data.get_top_genres(10)
    genre_options = ["All"] + top_genres

    selected_genre = st.selectbox(
        "Filter by Genre:",
        genre_options,
        help="Select a genre to filter movies or 'All' to view all movies"
    )

    genre_filter = None if selected_genre == "All" else selected_genre

    with st.spinner("Loading release data..."):
        try:
            releases_data = movie_data.releases(genre=genre_filter)

            st.write(f"Showing movie releases for: {'All Genres' if genre_filter is None else genre_filter}")

            if not releases_data.empty:
                st.bar_chart(
                    releases_data.set_index("Year")["Movie_Count"],
                    width=800,
                    height=400
                )

                st.write(f"Total movies: {releases_data['Movie_Count'].sum()}")

                peak_year = releases_data.loc[releases_data["Movie_Count"].idxmax()]
                st.write(f"Peak year: {peak_year['Year']} with {peak_year['Movie_Count']} movies")

            else:
                st.warning("No data available for the selected genre.")

        except Exception as e:
            st.error(f"Error analyzing movie releases: {e}")

    # --- SECTION 2: Actor Birth Statistics ---
    st.header("Actor Birth Statistics")

    time_unit = st.selectbox(
        "Group births by:",
        ["Year", "Month"],
        help="Choose whether to group actor births by year or month"
    )

    time_unit_code = "Y" if time_unit == "Year" else "M"

    with st.spinner("Loading birth statistics..."):
        try:
            birth_data = movie_data.ages(time_unit=time_unit_code)

            if not birth_data.empty:
                if time_unit == "Year":
                    st.bar_chart(
                        birth_data.set_index("Year")["Birth_Count"],
                        width=800,
                        height=400
                    )

                    earliest_year = birth_data["Year"].min()
                    latest_year = birth_data["Year"].max()
                    peak_year = birth_data.loc[birth_data["Birth_Count"].idxmax()]

                    st.write(f"Actor birth years range from {earliest_year} to {latest_year}")
                    st.write(f"Most births: {peak_year['Year']} with {peak_year['Birth_Count']} actors")

                else:
                    chart_data = birth_data.copy()
                    chart_data = chart_data.set_index("Month_Name")
                    st.bar_chart(
                        chart_data["Birth_Count"],
                        width=800,
                        height=400
                    )

                    peak_month = birth_data.loc[birth_data["Birth_Count"].idxmax()]
                    st.write(f"Most births: {peak_month['Month_Name']} with {peak_month['Birth_Count']} actors")

            else:
                st.warning("No birth data available.")

        except Exception as e:
            st.error(f"Error analyzing birth statistics: {e}")