import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("spotify_millsongdata.csv")

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower()

    # Check if required columns exist
    if "song" not in df.columns or "artist" not in df.columns:
        st.error("❌ Required columns ('song', 'artist') are missing in the dataset!")
        st.stop()

    # Clean text
    df["artist"] = df["artist"].str.strip().str.lower()
    df["song"] = df["song"].str.strip().str.lower()

    return df

df = load_data()

# TF-IDF Vectorization
@st.cache_resource
def train_model():
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(df["song"] + " " + df["artist"])

    # Use Nearest Neighbors instead of cosine_similarity
    model = NearestNeighbors(n_neighbors=6, metric="cosine", algorithm="brute")
    model.fit(tfidf_matrix)

    return model, tfidf_matrix, tfidf

model, tfidf_matrix, tfidf = train_model()

# Get song recommendations
def recommend_songs(song_name, num_recommendations=5):
    song_name = song_name.lower().strip()

    if song_name not in df["song"].values:
        return ["❌ Song not found in dataset"]

    song_idx = df[df["song"] == song_name].index[0]
    song_vec = tfidf.transform([df.iloc[song_idx]["song"] + " " + df.iloc[song_idx]["artist"]])

    distances, indices = model.kneighbors(song_vec, n_neighbors=num_recommendations + 1)
    recommended_songs = [df.iloc[i]["song"].title() for i in indices[0][1:]]

    return recommended_songs

# Streamlit UI
st.title("🎵 Song Recommendation System")

selected_artist = st.selectbox("Select an artist", sorted(df["artist"].unique()))
filtered_songs = df[df["artist"] == selected_artist]["song"].unique()
selected_song = st.selectbox("Choose a song", filtered_songs)

if st.button("Get Recommendations"):
    recommendations = recommend_songs(selected_song)
    st.write("### Recommended Songs:")
    for song in recommendations:
        st.write(f"🎶 {song}")


