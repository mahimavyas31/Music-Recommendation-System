import streamlit as st
import base64

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

# Call the function with your local image path
add_bg_from_local(r"C:\Users\USER\Desktop\PROject\spotify\app\3425171.jpg")

# ---------------- PAGE CONTENT ----------------
st.title("🎵 Spotify Recommendation System")
st.write("""
Welcome to the **Spotify Song Recommender** project.  
Navigate using the sidebar to:
- 🔍 Get song recommendations
- 📊 Explore dataset insights
- ℹ️ Learn more about the project
- 🎧 Access the Spotify API directly
""")

# Spotify logo image
st.image("https://storage.googleapis.com/pr-newsroom-wp/1/2023/05/Spotify-Logo.png", use_container_width=True)
