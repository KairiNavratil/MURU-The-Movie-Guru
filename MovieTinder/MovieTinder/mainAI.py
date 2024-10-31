import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
import numpy as np
from scipy.sparse import hstack, csr_matrix
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

# Assign weights to genres and keywords (you can tweak these values)
genre_weight = 0.8  # 70% weight for genres
keyword_weight = 0.2  # 30% weight for keywords



# Load the dataset (replace with the correct file path)
file_path = "C:/Users/kaijn/Downloads/MovieTinder/movies.csv"
movies = pd.read_csv(file_path)

# Step 2: Handle NaN or unexpected float values in the 'genres' column
movies['genres'] = movies['genres'].apply(lambda x: x.split('-') if isinstance(x, str) else [])



# Step 3: Use MultiLabelBinarizer to one-hot encode the split genres
mlb = MultiLabelBinarizer()
genre_matrix = mlb.fit_transform(movies['genres'])



# Step 4: Convert to DataFrame for easy viewing
genre_df = pd.DataFrame(genre_matrix, columns=mlb.classes_)




# Step 6: Print total counts of each genre
genre_totals = genre_df.sum()


# Step 7: Combine the one-hot encoded genres with the original dataset
# Resetting index of movies to avoid index conflicts
movies.reset_index(drop=True, inplace=True)
movies = pd.concat([movies, genre_df], axis=1)



# Step 8: Save the new dataset with one-hot encoded genres (optional)
movies.to_csv('movies_with_encoded_genres.csv', index=False)



# Step 2: Handle NaN or unexpected float values in the 'keywords' column
movies['keywords'] = movies['keywords'].apply(lambda x: x.split('-') if isinstance(x, str) else [])



mlb = MultiLabelBinarizer()
keyword_matrix = mlb.fit_transform(movies['keywords'])



# Step 4: Convert to DataFrame for easy viewing
keyword_df = pd.DataFrame(keyword_matrix, columns=mlb.classes_)


# Step 6: Print total counts of each keyword
keyword_totals = keyword_df.sum()

# Step 7: Combine the one-hot encoded keywords with the original dataset
# Resetting index of movies to avoid index conflicts
movies.reset_index(drop=True, inplace=True)
movies = pd.concat([movies, keyword_df], axis=1)


# Step 8: Save the new dataset with one-hot encoded keywords (optional)
movies.to_csv('movies_with_encoded_keywords.csv', index=False)

# Ensure all matrices are sparse and 2-D
def to_sparse_if_needed(matrix):
    return csr_matrix(matrix) if not isinstance(matrix, csr_matrix) else matrix

# Convert all matrices to sparse format if they aren't already
genre_matrix = to_sparse_if_needed(genre_matrix)
keywords_matrix = to_sparse_if_needed(keyword_matrix)


# Apply weights to genre and keyword matrices
weighted_genre_matrix = genre_matrix * genre_weight
weighted_keyword_matrix = keyword_matrix * keyword_weight


combined_features = hstack([
    weighted_genre_matrix, 
    weighted_keyword_matrix
]).tocsr()


scaler = MinMaxScaler()
normalized_features = scaler.fit_transform(combined_features.toarray())








# Calculate cosine similarity matrix
cosine_sim = cosine_similarity(combined_features)







def recommend_movies(liked_movies, disliked_movies=None, cosine_sim=cosine_sim, movies=movies, top_n=1):
    # Initialize similarity score arrays with zeros for both liked and disliked movies
    liked_sim_scores = np.zeros(len(movies))
    disliked_sim_scores = np.zeros(len(movies))

    # Calculate similarity for liked movies
    for movie_title in liked_movies:
        if movie_title in movies['title'].values:
            idx = movies[movies['title'] == movie_title].index[0]
            sim_scores = cosine_sim[idx]
            liked_sim_scores += sim_scores
        else:
            print(f"Movie '{movie_title}' not found in dataset.")

    # Calculate similarity for disliked movies (if any)
    if disliked_movies:
        for movie_title in disliked_movies:
            if movie_title in movies['title'].values:
                idx = movies[movies['title'] == movie_title].index[0]
                sim_scores = cosine_sim[idx]
                # Penalize similar movies by subtracting similarity scores
                disliked_sim_scores += sim_scores
            else:
                print(f"Movie '{movie_title}' not found in dataset.")
    
    # Combine the liked and disliked similarity scores
    combined_sim_scores = liked_sim_scores - disliked_sim_scores

    # Sort the combined similarity scores in descending order
    sim_scores = list(enumerate(combined_sim_scores))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the top_n most similar movies, excluding those in the input lists
    movie_indices = [
        i[0] for i in sim_scores if movies.iloc[i[0]]['title'] not in liked_movies + (disliked_movies or [])
    ][:top_n]

    # Return the top_n most similar movies
    return movies.iloc[movie_indices][['id']]

# This is the EVIL input ------------------------------------------------------

def recommend_movies_bad(disliked_movies, liked_movies=None, cosine_sim=cosine_sim, movies=movies, top_n=1):
    # Initialize similarity score arrays with zeros for both liked and disliked movies
    liked_sim_scores = np.zeros(len(movies))
    disliked_sim_scores = np.zeros(len(movies))

    # Calculate similarity for disliked movies
    for movie_title in disliked_movies:
        if movie_title in movies['title'].values:
            idx = movies[movies['title'] == movie_title].index[0]
            sim_scores = cosine_sim[idx]
            liked_sim_scores += sim_scores
        else:
            print(f"Movie '{movie_title}' not found in dataset.")

    # Calculate similarity for disliked movies (if any)
    if liked_movies:
        for movie_title in liked_movies:
            if movie_title in movies['title'].values:
                idx = movies[movies['title'] == movie_title].index[0]
                sim_scores = cosine_sim[idx]
                # Penalize similar movies by subtracting similarity scores
                disliked_sim_scores += sim_scores
            else:
                print(f"Movie '{movie_title}' not found in dataset.")
    
    # Combine the liked and disliked similarity scores
    combined_sim_scores = liked_sim_scores - disliked_sim_scores

    # Sort the combined similarity scores in descending order
    sim_scores = list(enumerate(combined_sim_scores))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the top_n most similar movies, excluding those in the input lists
    movie_indices = [
        i[0] for i in sim_scores if movies.iloc[i[0]]['title'] not in liked_movies + (disliked_movies or [])
    ][:top_n]

    # Return the top_n most similar movies
    return movies.iloc[movie_indices][['id']]



# Initialize a set to track displayed movie IDs
displayed_movies = set()

def get_random_movie_id():
    global displayed_movies
    
    # Filter out movies that have already been displayed
    available_movies = movies[~movies['id'].isin(displayed_movies)]
    
    # Check if there are any movies left to display
    if available_movies.empty:
        print("No more movies to display.")
        return None
    
    # Select a random movie ID from available movies
    random_movie = available_movies.sample(n=1)
    movie_id = random_movie.iloc[0]['id']
    
    # Add the displayed movie ID to the set
    displayed_movies.add(movie_id)
    
    return movie_id









# These are the arrays do add / change (string)
liked_movies = []
disliked_movies = []





# function commands + inputs -------------------------------

#recommended_movies = recommend_movies(liked_movies, disliked_movies, cosine_sim, movies, top_n=5)

#recommended_movies = recommend_movies_bad(disliked_movies, liked_movies, cosine_sim, movies, top_n=1) 

#random_movie_id = get_random_movie_id()
#if random_movie_id:
    #print(f"Random movie ID: {random_movie_id}")
