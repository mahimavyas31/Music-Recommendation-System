import streamlit as st

st.set_page_config(page_title="About Project", page_icon="ℹ️", layout="wide")

st.title("ℹ️ About this Project")

st.write("""
Website  Overview

The Spotify Recommendation System is an intelligent music recommendation platform designed to help users discover new songs based on their preferences. By analyzing musical features and user listening patterns, the system suggests songs that are most likely to match the user’s taste.
Unlike manually curated playlists, this system leverages machine learning and data analysis to provide personalized recommendations, improving the music discovery experience.

         
         
## The main goal of this project is to:

*Provide users with accurate song recommendations.
*Enhance user experience by creating personalized playlists.
*Analyze trends and patterns in music data such as genres, tempo, and mood.

### 📌 How it Works
1. Enter a song name (and optional artist).
2. The model finds the nearest neighbors using **cosine similarity**.
3. Top 10 similar tracks are recommended.

""")
