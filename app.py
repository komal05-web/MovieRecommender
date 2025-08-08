import streamlit as st
import pickle
import pandas as pd
import requests
import os
import gzip

# ------------------ Fetch Poster from TMDB API ------------------ #
def fetch_poster(movie_id):
    api_key = "a27779fccb907cb9f39e55f352d97ded"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    response = requests.get(url)

    if response.status_code != 200:
        st.error(f"TMDB API Error {response.status_code}: {response.text}")
        return "https://via.placeholder.com/500x750?text=No+Image"

    try:
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"http://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            st.warning("No poster found for this movie.")
            return "https://via.placeholder.com/500x750?text=No+Image"
    except Exception as e:
        st.error(f"Error parsing TMDB response: {e}")
        return "https://via.placeholder.com/500x750?text=No+Image"

# ------------------ Recommend Movies ------------------ #
def recommend(movie):
    if movie not in movies['title'].values:
        st.error(f"Movie '{movie}' not found in dataset.")
        st.stop()

    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error(f"Could not find index for movie '{movie}'.")
        st.stop()

    if len(similarity) != len(movies):
        st.error("Mismatch between similarity matrix and movie list.")
        st.stop()

    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommend_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommend_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))

    return recommend_movies, recommended_movies_posters

# ------------------ Load Movie Data ------------------ #
try:
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
except Exception as e:
    st.error(f"Failed to load movie_dict.pkl: {e}")
    st.stop()

# ------------------ Load Similarity Matrix ------------------ #
try:
    if os.path.exists('similarity.pkl'):
        with open('similarity.pkl', 'rb') as f:
            similarity = pickle.load(f)
    elif os.path.exists('similarity.pkl.gz'):
        with gzip.open('similarity.pkl.gz', 'rb') as f:
            similarity = pickle.load(f)
    else:
        st.error("Similarity file not found. Please check your deployment files.")
        st.stop()
except Exception as e:
    st.error(f"Failed to load similarity matrix: {e}")
    st.stop()

# ------------------ Streamlit UI ------------------ #
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    'Select a movie to get recommendations:',
    movies['title'].values
)

if st.button('Recommend'):
    st.write(f"Generating recommendations for: **{selected_movie_name}**")
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.text(names[idx])
            st.image(posters[idx])





