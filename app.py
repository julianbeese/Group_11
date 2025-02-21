import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.movie_dataset import MovieDataset

# initialising the class
try:
    dataset = MovieDataset()

except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()


# Streamlit App UI
st.title("🎬 Movie Data Analysis")

# --- SECTION 1: Movie Types ---
st.header("📊 Most Common Movie Types")

# Now Print the DataFrame and Graph
N = st.number_input("Select the Number to Display", min_value=1, max_value=50, step=1, value=10)
try:
    counting = dataset.movie_type(N)

    col1, col2 = st.columns(2)

    with col1: 
        # Dataframe for the genres
        st.write("Genre Counts")
        st.dataframe(counting, width= 500)

    with col2: 
        # Chart for the selected genres
        st.write("Top Genre Chart")
        st.bar_chart(counting.set_index("Genre"), width = 500, height = 400, horizontal= True)

except Exception as e:
    st.error(f"Error generating genre counts: {e}")

# --- SECTION 2: Actor Count Histogram ---
st.header("🎭 Number of Actors per Movie")

# calculating actor count
df_actor_count = dataset.actor_count()

# table
st.dataframe(df_actor_count)

# histogram
fig, ax = plt.subplots()
ax.bar(df_actor_count["Number_of_Actors"], df_actor_count["Movie_Count"], color="lightcoral")
ax.set_xlabel("Number of Actors")
ax.set_ylabel("Movie Count")
ax.set_title("Distribution of Number of Actors per Movie")
st.pyplot(fig)

# --- SECTION 3: Actor Height Distribution ---
st.header("📏 Actor Height Distribution")

gender_options = ["All"] + dataset.character_metadata["gender"].dropna().unique().tolist()
selected_gender = st.selectbox("Select gender:", gender_options)

min_height = st.number_input("Minimum height (cm):", min_value=0, max_value=300, value=150)
max_height = st.number_input("Maximum height (cm):", min_value=0, max_value=300, value=200)

# button
if st.button("Show Height Distribution"):
    df_actor_heights = dataset.actor_distributions(gender=selected_gender, min_height=min_height, max_height=max_height)

    st.dataframe(df_actor_heights)

    fig, ax = plt.subplots()
    ax.hist(df_actor_heights["height"], bins=30, edgecolor="black", color="green")
    ax.set_xlabel("Height (cm)")
    ax.set_ylabel("Frequency")
    ax.set_title(f"Height Distribution for {selected_gender}")
    st.pyplot(fig)
