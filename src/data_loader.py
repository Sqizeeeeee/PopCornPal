import pandas as pd
import os

def load_movielens_1m(data_dir='data/ml-1m'):
    ratings_file = os.path.join(data_dir, 'ratings.dat')
    movies_file = os.path.join(data_dir, 'movies.dat')

    ratings_cols = ['user_id', 'movie_id', 'rating', 'timestamp']
    movies_cols = ['movie_id', 'title', 'genres']

    # Dowload data
    ratings = pd.read_csv(ratings_file, sep='::', names=ratings_cols, engine='python')
    movies = pd.read_csv(movies_file, sep='::', names=movies_cols, engine='python', encoding='latin-1')

    # Checking and deleting data
    duplicates_ratings = ratings.duplicated().sum()
    # print(f"Duplicates ratings: {duplicates_ratings}")
    if duplicates_ratings > 0:
        ratings = ratings.drop_duplicates()
        # print("Duplicates in ratings are removed.")

    # checking duplicates in movies
    duplicates_movies = movies.duplicated().sum()
    # print(f"Duplicates in movies: {duplicates_movies}")
    if duplicates_movies > 0:
        movies = movies.drop_duplicates()
        # print("Duplicates in movies are removed.")

    # print('Example data with ratings:')
    # print(ratings.head())

    # print('\nExample data with films:')
    # print(movies.head())

    return ratings, movies


if __name__ == "__main__":
    load_movielens_1m()