import streamlit as st
import pandas as pd
import plotly.express as px
import speech_recognition as sr
import time
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Initialize Spotify API
SPOTIFY_CLIENT_ID = "8bf626ce626c40c78523f9a649bec8e0"
SPOTIFY_CLIENT_SECRET = "0fc65515fa2f4a909c55b97b4f070773"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, 
                                                           client_secret=SPOTIFY_CLIENT_SECRET))

# UI Enhancements
st.set_page_config(page_title="🎵 Music Recommendation App", layout="wide")

# Load dataset
csv_file = "spotify_millsongdata.csv"
if not os.path.exists(csv_file):
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    if uploaded_file:
        with open(csv_file, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("✅ File uploaded successfully!")

if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
    st.write("📊 Dataset Preview:", df.head())
else:
    st.error("❌ File is still missing. Please upload `spotify_millsongdata.csv`.")
    st.stop()

# Data Visualization
def visualize_data(df):
    st.subheader("🎵 Music Data Insights")
    top_artists = df['artist'].value_counts().head(10)
    fig_artist = px.bar(top_artists, x=top_artists.index, y=top_artists.values, title='🔥 Top 10 Artists')
    st.plotly_chart(fig_artist)

# Voice Search
def voice_search():
    st.subheader("🎤 Voice Search for Songs")
    try:
        import pyaudio
    except ImportError:
        st.error("🚨 PyAudio is not installed. Install it using `pip install pyaudio`.")
        return None
    
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎙️ Say the song name...")
        time.sleep(1)
        audio = r.listen(source)
    
    try:
        query = r.recognize_google(audio)
        st.success(f"🔍 Searching for: {query}")
        return query
    except sr.UnknownValueError:
        st.error("😕 Sorry, couldn't understand your voice.")
    except sr.RequestError:
        st.error("🚨 Could not request results, check your connection.")
    return None

# Fetch Spotify Song Preview
def fetch_spotify_preview(song, artist):
    query = f"track:{song} artist:{artist}"
    results = sp.search(q=query, type="track", limit=1)
    
    if results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        preview_url = track.get("preview_url")  # 30s audio preview
        spotify_url = track["external_urls"]["spotify"]  # Full track link
        return preview_url, spotify_url
    return None, None

# Music Player
def music_player():
    st.subheader("🎵 Music Streaming & Playback")
    song_choice = st.selectbox("Select a song:", df[['artist', 'song']].apply(lambda x: f"{x['artist']} - {x['song']}", axis=1))
    artist, song = song_choice.split(" - ", 1)
    
    preview_url, spotify_url = fetch_spotify_preview(song, artist)
    
    if preview_url:
        st.audio(preview_url, format="audio/mp3")
    else:
        st.warning("❌ No audio preview available.")
    
    if spotify_url:
        st.markdown(f'<a href="{spotify_url}" target="_blank">🎧 Listen on Spotify</a>', unsafe_allow_html=True)
    
    st.write(f"🎵 **Now Playing:** {song} by {artist}")

# Streamlit Tabs
st.title("🎵 Music Recommendation App")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Data Visualization", "🎙️ Voice Search", "📜 Lyrics Search", "❤️ Favorites", "🎧 Music Player"])

with tab1:
    visualize_data(df)

with tab2:
    voice_query = voice_search()
    if voice_query:
        results = df[df['song'].str.contains(voice_query, case=False, na=False)]
        st.write(results)

with tab3:
    search_query = st.text_input("Enter song lyrics to search:")
    if search_query:
        results = df[df['text'].str.contains(search_query, case=False, na=False)]
        st.write(results[['artist', 'song', 'text']])

with tab4:
    st.subheader("❤️ Your Favorite Songs")
    favorites = st.session_state.get("favorites", [])
    if favorites:
        st.write(pd.DataFrame(favorites, columns=["Artist", "Song"]))
    else:
        st.write("No favorites yet!")
    
    song_choice = st.selectbox("Select a song to add to favorites:", df[['artist', 'song']].apply(lambda x: f"{x['artist']} - {x['song']}", axis=1))
    if st.button("Add to Favorites"):
        artist, song = song_choice.split(" - ", 1)
        if "favorites" not in st.session_state:
            st.session_state["favorites"] = []
        st.session_state["favorites"].append((artist, song))
        st.success(f"Added {song} by {artist} to favorites!")

with tab5:
    music_player()
