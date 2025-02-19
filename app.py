import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.movie_dataset import MovieDataset

# initialising the class
dataset = MovieDataset()

# Streamlit App UI
st.title("🎬 Movie Data Analysis")

# --- SECTION 1: Movie Types ---
st.header("📊 Most Common Movie Types")

# input field
N = st.number_input("Select the number of top movie types:", min_value=1, max_value=50, value=10, step=1)
df_movie_types = dataset.movie_type(N)

# Table
st.dataframe(df_movie_types)

# histogram
fig, ax = plt.subplots()
ax.bar(df_movie_types["Movie_Type"], df_movie_types["Count"], color="skyblue")
ax.set_xlabel("Movie Type")
ax.set_ylabel("Count")
ax.set_title(f"Top {N} Most Common Movie Types")
plt.xticks(rotation=45, ha="right")
st.pyplot(fig)

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
