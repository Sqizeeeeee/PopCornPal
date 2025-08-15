import pandas as pd
import os

def load_movielens_1m(data_dir='data/ml-1m'):
    # Define file paths for ratings and movies data
    ratings_file = os.path.join(data_dir, 'ratings.dat')
    movies_file = os.path.join(data_dir, 'movies.dat')

    # Column names for ratings and movies datasets
    ratings_cols = ['user_id', 'movie_id', 'rating', 'timestamp']
    movies_cols = ['movie_id', 'title', 'genres']

    # Load ratings data from the file, using '::' as separator with Python engine
    ratings = pd.read_csv(ratings_file, sep='::', names=ratings_cols, engine='python')
    # Load movies data, specifying encoding to handle special characters
    movies = pd.read_csv(movies_file, sep='::', names=movies_cols, engine='python', encoding='latin-1')

    # Check for duplicate rows in ratings dataset
    duplicates_ratings = ratings.duplicated().sum()
    # If duplicates exist, remove them
    if duplicates_ratings > 0:
        ratings = ratings.drop_duplicates()

    # Check for duplicate rows in movies dataset
    duplicates_movies = movies.duplicated().sum()
    # If duplicates exist, remove them
    if duplicates_movies > 0:
        movies = movies.drop_duplicates()

    # Return cleaned dataframes for ratings and movies
    return ratings, movies


if __name__ == "__main__":
    # Call the function to load datasets (for testing purposes)
    load_movielens_1m()