import streamlit as st
import pandas as pd
import requests
from sklearn.neighbors import NearestNeighbors
import base64

# ---------------------- Spotify API Setup ----------------------
CLIENT_ID = "your_client_id"         # <- Replace this
CLIENT_SECRET = "your_client_secret" # <- Replace this

@st.cache_resource
def get_token():
    url = "https://accounts.spotify.com/api/token"
    response = requests.post(url, {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    })
    return response.json().get("access_token")

def get_spotify_url(song, artist=""):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    query = f"track:{song}"
    if artist:
        query += f" artist:{artist}"

    url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=1"
    response = requests.get(url, headers=headers).json()

    if response.get("tracks") and response["tracks"]["items"]:
        track_id = response["tracks"]["items"][0]["id"]
        return f"https://open.spotify.com/track/{track_id}"
    return None

# ---------------------- Streamlit UI Setup ----------------------
st.set_page_config(page_title="Spotify Recommendation System", page_icon="🎶", layout="wide")

def add_bg_from_local(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_from_local(r"C:\Users\USER\Desktop\PROject\spotify\app\3425171.jpg")

# ---------------------- Load Dataset ----------------------
@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\USER\Desktop\PROject\spotify\DATA\dataset.csv")
    return df

df = load_data()
feature_cols = ["danceability", "energy", "valence", "tempo", "acousticness",
                "liveness", "instrumentalness", "loudness", "speechiness"]
feature_cols = [c for c in feature_cols if c in df.columns]
X = df[feature_cols].values

@st.cache_resource
def build_knn():
    knn = NearestNeighbors(n_neighbors=10, metric="cosine")
    knn.fit(X)
    return knn

knn = build_knn()

df["track_name"] = df["track_name"].astype(str).str.strip().str.lower()
df["artists"] = df["artists"].astype(str).str.strip().str.lower()

def find_track_index(query_track, query_artist=None):
    q = query_track.strip().lower()
    if query_artist:
        mask = (df["track_name"] == q) & (df["artists"] == query_artist.strip().lower())
    else:
        mask = df["track_name"] == q

    matches = df[mask]
    if matches.empty:
        matches = df[df["track_name"].str.contains(q)]
    return matches.index[0] if not matches.empty else None

def recommend_songs(track_name, artist=None, k=10):
    idx = find_track_index(track_name, artist)
    if idx is None:
        return pd.DataFrame()

    distances, indices = knn.kneighbors(X[idx].reshape(1, -1), n_neighbors=k + 1)
    rec_idx = [i for i in indices.flatten() if i != idx][:k]
    return df.iloc[rec_idx][["track_name", "artists"]]

# ---------------------- UI ----------------------
st.title("🎶 Spotify Recommendation System")
st.write("Find 10 similar songs based on audio features!")

song = st.text_input("Enter a Song Name:", "Blinding Lights")
artist = st.text_input("(Optional) Enter Artist Name:")


demo_spotify_links = {
    "blinding lights": "https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b",
    "shape of you": "https://open.spotify.com/track/7qiZfU4dY1lWllzX7mPBI3",
    "someone you loved": "https://open.spotify.com/track/7qEHsqek33rTcFNT9PFqLf",
    "drivers license": "https://open.spotify.com/track/5wANPM4fQCJwkGd4rN57mH"
}

if st.button("Recommend"):
    recs = recommend_songs(song, artist)

    if recs.empty:
        st.warning("❌ Song not found in dataset")
    else:
        st.success("✅ Here are your recommendations:")

        for _, row in recs.reset_index(drop=True).iterrows():
            track = row["track_name"].title()
            artist_name = row["artists"].title()
            st.markdown(f"🎵 <b>{track}</b> by <i>{artist_name}</i>", unsafe_allow_html=True)

            # --- Get Spotify URL ---
            spotify_url = get_spotify_url(track, artist_name)

            # Fallback to demo link
            if not spotify_url:
                spotify_url = demo_spotify_links.get(track.lower())
