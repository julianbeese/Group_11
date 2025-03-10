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

3. Genre Classification:
   - Uses a local LLM to classify movie genres based on summaries
   - Compares LLM classifications with actual genres from the database
"""

import ast
import numpy as np
import pandas as pd
import random
import requests
import streamlit as st
import time

from src.movie_dataset import MovieDataset

# Load data
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
page = st.sidebar.radio("Go to", ["Main Dashboard", "Chronological Analysis", "Genre Classification"])


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
        # Set plot title
        st.header("Most Common Movie Types")

        # Initiate display of plot for most common movie types with error handling
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
        # Set plot title
        st.header("Number of Actors per Movie")

        # Get data
        df_actor_count = movie_dataset.actor_count()

        # Create figure
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

        # Set plot title
        st.header("Actor Height Distribution")

        # Get unique gender options from the dataset (including: "All")
        gender_options = ["All"] + movie_dataset.character_metadata[
            "actor_gender"
        ].dropna().astype(str).unique().tolist()

        # Allow user to select gender
        selected_gender = st.selectbox("Select gender:", gender_options)

        # Update the min/max values to be more appropriate for heights in cm
        min_height = st.number_input(
            "Minimum height (cm):", min_value=0, max_value=300, value=150
        )
        max_height = st.number_input(
            "Maximum height (cm):", min_value=0, max_value=300, value=200
        )

        # Process data if button is clicked
        if st.button("Show Height Distribution"):
            df_actor_heights = movie_dataset.actor_distributions(
                gender=selected_gender, min_height=min_height, max_height=max_height
            )

            # Display number of records found for selected criteria
            st.write(
                f"Actor Height Distribution for {selected_gender} - {len(df_actor_heights)} records found"
            )

            # Extract height values from the dataset
            heights = df_actor_heights["actor_height"].values

            if len(heights) > 0:
                # Determine number of bins for the histogram
                num_bins = min(30, len(heights))

                # Compute histogram
                hist, bins = np.histogram(heights, bins=num_bins)

                # Compute bin centers for better visualization
                bin_centers = (bins[:-1] + bins[1:]) / 2
                bin_centers = np.round(bin_centers, 1)

                # Create dataframe for plotting
                hist_df = pd.DataFrame({"height_bin": bin_centers, "count": hist})

                # Display bar chart
                st.bar_chart(hist_df.set_index("height_bin"), height=400)

                # Display height statistics
                st.write("Height Statistics (cm):")
                st.write(f"Average: {heights.mean():.1f} cm")
                st.write(f"Minimum: {heights.min():.1f} cm")
                st.write(f"Maximum: {heights.max():.1f} cm")

            else:
                # Show a warning if no data matches the selected criteria
                st.warning("No data available for the selected criteria.")

    # Call functions to show different sections of the app
    display_movie_types_section(movie_data)
    display_actor_count_section(movie_data)
    display_height_distribution_section(movie_data)


# --- CHRONOLOGICAL ANALYSIS PAGE ---
elif page == "Chronological Analysis":
    st.title("Movie Data Analysis - Chronological Analysis")

    # --- SECTION 1: Movie Releases by Year ---
    st.header("Movie Releases by Year")

    # Get top 10 movie genres
    top_genres = movie_data.get_top_genres(10)

    # Add option "All" to allow viewing all movies regardless of genre
    genre_options = ["All"] + top_genres

    # Dropdown to filter movies by genre
    selected_genre = st.selectbox(
        "Filter by Genre:",
        genre_options,
        help="Select a genre to filter movies or 'All' to view all movies"
    )

    # Determine the genre filter based on user selection
    genre_filter = None if selected_genre == "All" else selected_genre

    # Display a spinner while loading data
    with st.spinner("Loading release data..."):
        try:
            # Retrieve movie release data based on selected genre
            releases_data = movie_data.releases(genre=genre_filter)

            # Display the selected genre filter
            st.write(f"Showing movie releases for: {'All Genres' if genre_filter is None else genre_filter}")

            if not releases_data.empty:
                # Display bar chart of movie releases by year
                st.bar_chart(
                    releases_data.set_index("Year")["Movie_Count"],
                    width=800,
                    height=400
                )

                # Show total number of movies
                st.write(f"Total movies: {releases_data['Movie_Count'].sum()}")

                # Identify the peak year with the highest number of movie releases
                peak_year = releases_data.loc[releases_data["Movie_Count"].idxmax()]
                st.write(f"Peak year: {peak_year['Year']} with {peak_year['Movie_Count']} movies")

            else:
                # Display warning if no data is available
                st.warning("No data available for the selected genre.")

        except Exception as e:
            # Error handling
            st.error(f"Error analyzing movie releases: {e}")

    # --- SECTION 2: Actor Birth Statistics ---
    st.header("Actor Birth Statistics")

    # Dropdown to select time for grouping births
    time_unit = st.selectbox(
        "Group births by:",
        ["Year", "Month"],
        help="Choose whether to group actor births by year or month"
    )

    # Convert time unit selection to appropiate format
    time_unit_code = "Y" if time_unit == "Year" else "M"

    # Display spinner while loading data
    with st.spinner("Loading birth statistics..."):
        try:
            # Retrieve actor birth data based on selected time unit and display bar chart
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
                    # Prepare data for displaying actor births by month and display as bar chart
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
                # Display warning if no data is available
                st.warning("No birth data available.")

        except Exception as e:

            # Handle errors and display error message
            st.error(f"Error analyzing birth statistics: {e}")

# --- GENRE CLASSIFICATION PAGE ---
elif page == "Genre Classification":
    st.title("Movie Genre Classification with LLM")


    def classify_with_llm(title, summary, actors, release_year=None):
        """
        Classify movie genres using local Ollama LLM based on all available movie information.

        Args:
            title (str): Movie title
            summary (str): Movie summary (generated)
            actors (list): List of actors in the movie
            release_year (str, optional): Year the movie was released

        Returns:
            tuple: (predicted_genres, raw_response)
        """
        url = "http://localhost:11434/api/generate"

        # Build a rich context for the LLM
        year_info = f"Release Year: {release_year}\n" if release_year else ""
        cast_info = f"Cast: {', '.join(actors)}\n" if actors else ""

        prompt = f"""You are a movie genre classifier. Given information about a movie, your task is to predict its genres.

Movie Title: {title}
{year_info}{cast_info}Movie Description: {summary}

Based on this information, identify the most appropriate genres for this movie.
Output ONLY a comma-separated list of genres (e.g., "Drama, Thriller, Mystery").
Do not include any explanations, just return the genres.
Be specific and try to match standard movie genres like Action, Comedy, Drama, Horror, Sci-Fi, Fantasy, Romance, Thriller, Mystery, Adventure, Animation, Documentary, etc.
Do not prefix with phrases like "Genres:", just list the genres directly.
"""

        try:
            response = requests.post(
                url,
                json={
                    "model": "mistral",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                genres_text = result.get('response', '').strip()
                predicted_genres = [genre.strip() for genre in genres_text.split(',')]
                return predicted_genres, genres_text
            else:
                return [], f"Error: {response.status_code} - {response.text}"

        except requests.exceptions.RequestException as e:
            return [], f"Error connecting to Ollama: {str(e)}"


    def verify_genres_with_llm(actual_genres, predicted_genres):
        """
        Ask the LLM to verify if the predicted genres match the actual genres.

        Args:
            actual_genres (list): List of actual genres
            predicted_genres (list): List of predicted genres

        Returns:
            tuple: (is_match, explanation)
        """
        url = "http://localhost:11434/api/generate"

        prompt = f"""Compare these two lists of movie genres and determine if the predicted genres are accurate.

Actual Genres: {', '.join(actual_genres)}
Predicted Genres: {', '.join(predicted_genres)}

Respond with either "YES" or "NO" followed by a brief explanation on a new line.
- If most of the predicted genres appear in the actual genres, respond with "YES".
- If few or none of the predicted genres appear in the actual genres, respond with "NO".
"""

        try:
            response = requests.post(
                url,
                json={
                    "model": "mistral",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                verification = result.get('response', '').strip()

                is_match = verification.upper().startswith("YES")

                return is_match, verification
            else:
                return False, f"Error: {response.status_code} - {response.text}"

        except requests.exceptions.RequestException as e:
            return False, f"Error connecting to Ollama: {str(e)}"


    def compare_genres(actual_genres, predicted_genres):
        """
        Compare predicted genres with actual genres and determine if there's a match.

        Args:
            actual_genres (list): List of actual genres
            predicted_genres (list): List of predicted genres

        Returns:
            tuple: (matches, non_matches, match_percentage)
        """
        actual_lower = [g.lower() for g in actual_genres]
        predicted_lower = [g.lower() for g in predicted_genres]

        matches = [g for g in predicted_lower if g in actual_lower]
        non_matches = [g for g in predicted_lower if g not in actual_lower]

        if predicted_lower:
            match_percentage = (len(matches) / len(predicted_lower)) * 100
        else:
            match_percentage = 0

        return matches, non_matches, match_percentage

    if 'movie_title' not in st.session_state:
        st.session_state.movie_title = ""
        st.session_state.movie_summary = ""
        st.session_state.movie_actors = []
        st.session_state.release_year = ""
        st.session_state.actual_genres = []
        st.session_state.predicted_genres = []
        st.session_state.comparison_result = None
        st.session_state.verification_result = None

    if st.button("🔄 Shuffle Movie"):
        with st.spinner("Selecting a random movie..."):
            random_movie = movie_data.get_random_movie()
            if random_movie:
                st.session_state.movie_title = random_movie["title"]
                st.session_state.movie_summary = random_movie["summary"]
                st.session_state.movie_actors = random_movie["actors"]
                st.session_state.release_year = random_movie.get("release_year", "")
                st.session_state.actual_genres = random_movie["genres"]
                st.session_state.predicted_genres = []
                st.session_state.comparison_result = None
                st.session_state.verification_result = None
            else:
                st.error("Failed to find a suitable movie. Please try again.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Movie Information")
        st.markdown(f"**Title:** {st.session_state.movie_title}")

        if st.session_state.release_year:
            st.markdown(f"**Year:** {st.session_state.release_year}")

        if st.session_state.movie_actors:
            st.markdown("**Cast:**")
            actors_text = ", ".join(st.session_state.movie_actors)
            st.markdown(actors_text)

        st.text_area(
            "Movie Description",
            value=st.session_state.movie_summary,
            height=250,
            disabled=True
        )

    with col2:
        st.subheader("Genre Analysis")

        actual_genres_str = ", ".join(
            st.session_state.actual_genres) if st.session_state.actual_genres else "No genres available"
        st.text_area(
            "Actual Genres (from Database)",
            value=actual_genres_str,
            height=80,
            disabled=True
        )

        if st.session_state.movie_title and not st.session_state.predicted_genres:
            with st.spinner("Classifying with LLM..."):
                st.session_state.predicted_genres, raw_response = classify_with_llm(
                    st.session_state.movie_title,
                    st.session_state.movie_summary,
                    st.session_state.movie_actors,
                    st.session_state.release_year
                )

                if st.session_state.predicted_genres:
                    matches, non_matches, match_percentage = compare_genres(
                        st.session_state.actual_genres,
                        st.session_state.predicted_genres
                    )
                    st.session_state.comparison_result = (matches, non_matches, match_percentage)

                    is_match, explanation = verify_genres_with_llm(
                        st.session_state.actual_genres,
                        st.session_state.predicted_genres
                    )
                    st.session_state.verification_result = (is_match, explanation)

        predicted_genres_str = ", ".join(
            st.session_state.predicted_genres) if st.session_state.predicted_genres else "No predictions yet"
        st.text_area(
            "Predicted Genres (from LLM)",
            value=predicted_genres_str,
            height=80,
            disabled=True
        )

        if st.session_state.comparison_result:
            matches, non_matches, match_percentage = st.session_state.comparison_result

            st.markdown("#### Comparison Results")
            if matches:
                st.markdown(f"✅ **Matching genres:** {', '.join(matches)}")
            if non_matches:
                st.markdown(f"❌ **Non-matching genres:** {', '.join(non_matches)}")

            st.progress(match_percentage / 100)
            st.markdown(f"**Match accuracy:** {match_percentage:.1f}%")

            if st.session_state.verification_result:
                is_match, explanation = st.session_state.verification_result

                st.markdown("#### LLM Verification")
                if is_match:
                    st.success(explanation)
                else:
                    st.error(explanation)

    # Instructions and information about the classification
    with st.expander("ℹ️ About this Classification"):
        st.markdown("""
        ### How it works

        This page uses a local LLM (Large Language Model) to classify movie genres based on available information:

        1. **Random Selection**: Click "Shuffle Movie" to select a random movie from the dataset.
        2. **LLM Classification**: The system automatically sends the movie information to a local LLM to predict genres.
        3. **Comparison**: The predicted genres are compared with the actual genres from the database.
        4. **Verification**: A second LLM query verifies if the predictions match the actual genres.

        ### Prerequisites

        To use this feature, you need:

        - [Ollama](https://ollama.ai/) installed and running locally
        - A small language model 'mistral' pulled into Ollama

        Run these commands to get started:
        ```bash
        # Install Ollama (if not already installed)
        curl -fsSL https://ollama.ai/install.sh | sh

        # Pull a small model
        ollama pull llama3
        ```

        ### Note

        Since we don't have actual plot summaries that match the movie IDs in our dataset, 
        we generate descriptions based on the available movie metadata. This means the 
        descriptions are not the actual movie plots but rather synthesized information 
        to help the LLM make better genre predictions.
        """)
