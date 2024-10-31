import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
import numpy as np
from scipy.sparse import hstack, csr_matrix
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

def find_row(movie_id):
    return movies[movies['id'] == movie_id].iloc[0]

# Assign weights to genres and keywords
genre_weight = 0.8  # 80% weight for genres
keyword_weight = 0.2  # 20% weight for keywords

# Load the dataset (replace with your file path)
file_path = "C:/Users/kaijn/Downloads/MovieTinder/movies.csv"
movies = pd.read_csv(file_path)

# Step 2: Handle NaN or unexpected float values in the 'genres' column
movies['genres'] = movies['genres'].apply(lambda x: x.split('-') if isinstance(x, str) else [])

# Step 3: One-hot encode the 'genres' column
mlb = MultiLabelBinarizer()
genre_matrix = mlb.fit_transform(movies['genres'])
genre_df = pd.DataFrame(genre_matrix, columns=mlb.classes_)

# Step 4: Handle NaN or unexpected float values in the 'keywords' column
movies['keywords'] = movies['keywords'].apply(lambda x: x.split('-') if isinstance(x, str) else [])

# One-hot encode the 'keywords' column
mlb = MultiLabelBinarizer()
keyword_matrix = mlb.fit_transform(movies['keywords'])
keyword_df = pd.DataFrame(keyword_matrix, columns=mlb.classes_)

# Combine one-hot encoded genres and keywords with the original dataset
movies.reset_index(drop=True, inplace=True)
movies = pd.concat([movies, genre_df, keyword_df], axis=1)

# Save the new dataset (optional)
movies.to_csv('movies_with_encoded_genres_keywords.csv', index=False)

# Ensure all matrices are sparse and 2-D
def to_sparse_if_needed(matrix):
    return csr_matrix(matrix) if not isinstance(matrix, csr_matrix) else matrix

# Convert genre and keyword matrices to sparse format
genre_matrix = to_sparse_if_needed(genre_matrix)
keyword_matrix = to_sparse_if_needed(keyword_matrix)

# Apply weights to genre and keyword matrices
weighted_genre_matrix = genre_matrix * genre_weight
weighted_keyword_matrix = keyword_matrix * keyword_weight

# Combine the weighted genre and keyword matrices
combined_features = hstack([weighted_genre_matrix, weighted_keyword_matrix]).tocsr()

# Normalize the features
scaler = MinMaxScaler()
normalized_features = scaler.fit_transform(combined_features.toarray())


# Function to recommend movies based on liked and disliked movies
def recommend_movies(liked_movies, disliked_movies=None, cosine = cosine_similarity, movies=movies, top_n=1):
    liked_sim_scores = np.zeros(len(movies))
    disliked_sim_scores = np.zeros(len(movies))
    cosine_sim = cosine_similarity(normalized_features)
    # Calculate similarity for liked movies
    for movie_title in liked_movies:
        if movie_title in movies['title'].values:
            idx = movies[movies['title'] == movie_title].index[0]
            sim_scores = cosine_sim[idx]
            liked_sim_scores += sim_scores
        else:
            print(f"Movie '{movie_title}' not found in dataset.")

    # Calculate similarity for disliked movies
    if disliked_movies:
        for movie_title in disliked_movies:
            if movie_title in movies['title'].values:
                idx = movies[movies['title'] == movie_title].index[0]
                sim_scores = cosine_sim[idx]
                disliked_sim_scores += sim_scores

    # Combine the liked and disliked similarity scores
    combined_sim_scores = liked_sim_scores - disliked_sim_scores

    # Sort the combined similarity scores in descending order
    sim_scores = list(enumerate(combined_sim_scores))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the top N most similar movies, excluding those in liked or disliked movies
    movie_indices = [i[0] for i in sim_scores if movies.iloc[i[0]]['title'] not in liked_movies + (disliked_movies or [])][:top_n]

    # Return the top N most similar movies
    return movies.iloc[movie_indices][['poster_path']]

# Function to recommend movies based on disliked movies (alternative)
def recommend_movies_bad(disliked_movies, liked_movies=None, cosine_sim = cosine_similarity, movies=movies, top_n=1):
    liked_sim_scores = np.zeros(len(movies))
    disliked_sim_scores = np.zeros(len(movies))
    cosine_sim = cosine_similarity(normalized_features)

    # Calculate similarity for disliked movies
    for movie_title in disliked_movies:
        if movie_title in movies['title'].values:
            idx = movies[movies['title'] == movie_title].index[0]
            sim_scores = cosine_sim[idx]
            liked_sim_scores += sim_scores

    # Calculate similarity for liked movies (if any)
    if liked_movies:
        for movie_title in liked_movies:
            if movie_title in movies['title'].values:
                idx = movies[movies['title'] == movie_title].index[0]
                sim_scores = cosine_sim[idx]
                disliked_sim_scores += sim_scores

    # Combine the liked and disliked similarity scores
    combined_sim_scores = liked_sim_scores - disliked_sim_scores

    # Sort the combined similarity scores in descending order
    sim_scores = list(enumerate(combined_sim_scores))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the top N most similar movies, excluding those in liked or disliked movies
    movie_indices = [i[0] for i in sim_scores if movies.iloc[i[0]]['title'] not in liked_movies + (disliked_movies or [])][:top_n]

    # Return the top N most similar movies
    return movies.iloc[movie_indices][['poster_path']]

# Function to get a random movie ID (exclude already displayed movies)
displayed_movies = set()
def get_random_movie_id():
    global displayed_movies
    available_movies = movies[~movies['id'].isin(displayed_movies)]
    if available_movies.empty:
        print("No more movies to display.")
        return None
    random_movie = available_movies.sample(n=1)
    movie_id = random_movie.iloc[0]['id']
    displayed_movies.add(movie_id)
    return movie_id
