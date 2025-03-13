import streamlit as st

st.set_page_config(page_title="Movie Recommender", layout="wide")

import pickle
import gdown
import pandas as pd
import requests
import os


# Function to fetch movie details including poster, genres, production companies, and overview
def fetch_movie_details(movie_id):
    api_key = "fea08e12ca9ee23ed757a2e06ad9ed79"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
    response = requests.get(url).json()
    
    # Extract movie details
    poster_url = f"https://image.tmdb.org/t/p/w500{response.get('poster_path', '')}"
    genres = ", ".join([genre["name"] for genre in response.get("genres", [])])
    overview = response.get("overview", "No overview available.")
    production_companies = ", ".join([company["name"] for company in response.get("production_companies", [])])

    return poster_url, genres, overview, production_companies

# Function to recommend movies
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    recommended_genres = []
    recommended_overviews = []
    recommended_productions = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        title = movies.iloc[i[0]].title

        # Fetch movie details
        poster, genres, overview, production = fetch_movie_details(movie_id)

        recommended_movies.append(title)
        recommended_posters.append(poster)
        recommended_genres.append(genres)
        recommended_overviews.append(overview)
        recommended_productions.append(production)

    return recommended_movies, recommended_posters, recommended_genres, recommended_overviews, recommended_productions

# Load saved data
movies_url = "https://drive.google.com/uc?id=1T5Nfi3hClK5QzGr8IbRCubIgPD0wot_Z"
similarity_url = "https://drive.google.com/uc?id=1bShhUHlCWzrm0qEIPkQ62xK0c0Dhpc8V"

@st.cache_data  # Cache the download to prevent repeated downloads
def download_files():
    if not os.path.exists("movies_dict.pkl"):
        gdown.download(movies_url, "movies_dict.pkl", fuzzy=True, quiet=False)
    if not os.path.exists("similarity.pkl"):
        gdown.download(similarity_url, "similarity.pkl", fuzzy=True, quiet=False)

# Run download only once
download_files()

# Load Pickle Files
movies_dict = pickle.load(open("movies_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open("similarity.pkl", "rb"))



# Custom CSS for styling
st.markdown("""
    <style>
        .main-content {
            color: white;
        }
        .stApp {
            background-color: #121212;
        }
        .movie-card {
            background-color: #1c1c1c;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        .movie-title {
            font-weight: bold;
            text-align: center;
            margin-top: 5px;
        }
        .genre-text {
            font-size: 14px;
            font-family: 'Courier New', monospace;
            color: #f5c518;
        }
        .overview-text {
            font-size: 13px;
            font-family: 'Georgia', serif;
            color: #bbb;
        }
        .production-text {
            font-size: 13px;
            font-family: 'Verdana', sans-serif;
            color: #ff9800;
        }
        .stButton>button {
            background-color: #f5c518;
            color: black;
            font-weight: bold;
            width: 100%;
        }
        div[data-testid="stVerticalBlock"] {
            gap: 0rem;
        }
    </style>
""", unsafe_allow_html=True)

# Create a two-column layout using Streamlit's native column system
left_col, right_col = st.columns([1, 3])

# Left column (Search and Selection)
with left_col:
    # Title and logo
    st.image("https://upload.wikimedia.org/wikipedia/commons/6/69/IMDB_Logo_2016.svg", width=100)
    st.markdown("<h1 style='color: white; font-size: 24px;'>Movie Recommender System</h1>", unsafe_allow_html=True)
    
    # Selection box
    selected_movie_name = st.selectbox("Select a movie:", movies['title'].values)
    
    # Recommend button
    if st.button("Recommend", key="recommend"):
        st.session_state["recommend_clicked"] = True
        st.session_state["selected_movie"] = selected_movie_name

# Right column (Movie Recommendations)
with right_col:
    # Create a container for recommendations
    recommendation_container = st.container()
    
    # Display recommendations if button was clicked
    if st.session_state.get("recommend_clicked", False):
        with recommendation_container:
            st.markdown("<h2 style='color: white;'>Recommended Movies</h2>", unsafe_allow_html=True)
            
            names, posters, genres, overviews, productions = recommend(st.session_state.get("selected_movie"))
            
            # Display recommendations in a grid of 5 columns
            movie_cols = st.columns(5)
            
            for i in range(5):
                with movie_cols[i]:
                    st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                    st.image(posters[i])
                    st.markdown(f'<p class="movie-title">{names[i]}</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="genre-text"><b>Genre:</b> {genres[i]}</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="overview-text"><b>Overview:</b> {overviews[i][:100]}...</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="production-text"><b>Production:</b> {productions[i]}</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)