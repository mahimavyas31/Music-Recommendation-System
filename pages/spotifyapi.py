
import streamlit as st
import base64
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Spotify Recommender", page_icon="🎶", layout="wide")

# ---------------- BACKGROUND IMAGE ----------------
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

# ---------------- SPOTIFY API AUTH ----------------
client_id = "2c021b923dfc4db18fa8eb39033c47d4"    
client_secret = "61e8ab2db9044f84a0824b809c6a8c9e"   

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
))

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\USER\Desktop\PROject\spotify\DATA\dataset.csv")
    features = ['danceability','energy','valence','tempo',
                'acousticness','liveness','instrumentalness','loudness']
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df[features])
    return df, df_scaled, features

df, df_scaled, features = load_data()

# Fit Nearest Neighbors model
model = NearestNeighbors(n_neighbors=6, metric='cosine')
model.fit(df_scaled)

# ---------------- FUNCTIONS ----------------
def get_song_features(song_name, artists=None):
    query = song_name
    if artists:
        query += f" artist:{artists}"

    result = sp.search(q=query, type="track", limit=1)
    if not result["tracks"]["items"]:
        return None

    track = result["tracks"]["items"][0]
    track_id = track["id"]

    # Handle 403 error gracefully
    try:
        features_spotify = sp.audio_features([track_id])[0]
        if not features_spotify:
            raise Exception("No audio features available")
        features_list = [features_spotify[f] for f in features]
    except:
        
        features_list = [0]*len(features)  # fallback

    song_data = {
        "track_name": track["name"],
        "artists": track["artists"][0]["name"],
        "id": track_id,
        "preview_url": track["preview_url"],
        "features": features_list
    }
    return song_data

def recommend_from_dataset(song_features, n=5):
    distances, indices = model.kneighbors([song_features])
    recs = df.iloc[indices[0][1:n+1]][['track_name','artists']]
    return recs

def get_track_id(song_name, artists):
    """Get Spotify track ID for embedding"""
    query = f"{song_name} artist:{artists}"
    result = sp.search(q=query, type="track", limit=1)
    if result["tracks"]["items"]:
        return result["tracks"]["items"][0]["id"]
    return None

# ---------------- PAGE CONTENT ----------------
st.title("🎵 Spotify Recommendation System")
st.write("""
Welcome to the *Spotify Song Recommender* project.  
Enter a song below to get recommendations based on *Spotify API features* + *ML model*.
""")

song_name = st.text_input("Enter a song name")
artists = st.text_input("Enter artist name (optional)")

if st.button("Recommend"):
    song_data = get_song_features(song_name,artists)
    if song_data:
        st.success(f"🎵 Found: {song_data['track_name']} by {song_data['artists']}")

        # 1️⃣ Show preview audio (30 sec)
        if song_data["preview_url"]:
            st.audio(song_data["preview_url"])
        
            

        # 2️⃣ Embed Spotify Player
        embed_url = f"https://open.spotify.com/embed/track/{song_data['id']}"
        st.markdown(
            f"""
            <iframe src="{embed_url}" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>
            """,
            unsafe_allow_html=True
        )

        # Get recommendations
        recs = recommend_from_dataset(song_data['features'], n=5)
        st.subheader("Recommended Songs:")
        for idx, row in recs.iterrows():
            rec_track_id = get_track_id(row['track_name'], row['artists'])
            if rec_track_id:
                rec_embed = f"https://open.spotify.com/embed/track/{rec_track_id}"
                st.markdown(
                    f"- {row['track_name']} by {row['artists']}<br>"
                    f"<iframe src='{rec_embed}' width='300' height='80' frameborder='0' allowtransparency='true' allow='encrypted-media'></iframe>",
                    unsafe_allow_html=True
                )
            else:
                st.write(f"- {row['track_name']} by {row['artists']} (No Spotify embed available)")
    else:
        st.error("❌ Song not found in Spotify API")