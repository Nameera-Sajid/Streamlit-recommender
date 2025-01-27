from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import pandas as pd

# Load dataset
@st.cache_data
def load_data():
    data = pd.read_csv("spotify_millsongdata.csv")
    data['artist'] = data['artist'].str.strip().str.lower()  # Normalize artist names
    return data

data = load_data()

# User input
st.title("Song Recommendation System")
artist_names = data['artist'].unique()
selected_artist = st.selectbox("Select an artist", artist_names)

if selected_artist:
    # Create TF-IDF matrix using artist data
    tfidf = TfidfVectorizer(stop_words='english', max_features=1000, ngram_range=(1, 2))
    tfidf_matrix = tfidf.fit_transform(data['artist'])

    # Compute cosine similarity for the selected artist
    artist_index = data[data['artist'] == selected_artist].index[0]
    cosine_sim = cosine_similarity(tfidf_matrix[artist_index], tfidf_matrix, dense_output=False)

    # Sort similarity scores and filter out the same artist
    similarity_scores = cosine_sim.toarray()[0]
    sorted_scores = sorted(enumerate(similarity_scores), key=lambda x: x[1], reverse=True)
    top_indices = [i[0] for i in sorted_scores if data.iloc[i[0]]['artist'] != selected_artist][:5]

    # Display recommendations
    recommended_songs = data.iloc[top_indices]
    st.subheader(f"Top Recommendations for Artist: {selected_artist.title()}")
    st.write(recommended_songs[['artist']])
