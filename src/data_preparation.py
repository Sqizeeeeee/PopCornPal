import pandas as pd
from sklearn.model_selection import train_test_split
from data_loader import load_movielens_1m

def clean_data(ratings, movies):
    """
    Remove duplicates and missing values from the data.
    Returns cleaned ratings and movies DataFrames.
    """
    # Drop duplicate rows from ratings and movies
    ratings = ratings.drop_duplicates()
    movies = movies.drop_duplicates()

    # Drop rows with missing values if any in ratings
    if ratings.isnull().any().any():
        ratings = ratings.dropna()

    # Drop rows with missing values if any in movies
    if movies.isnull().any().any():
        movies = movies.dropna()

    return ratings, movies

def encode_ids(ratings):
    """
    Convert user_id and movie_id to numerical indices (user_idx and movie_idx).
    This is necessary for modeling, which requires numeric IDs.
    Returns the updated ratings DataFrame along with original index objects.
    """
    ratings['user_idx'], user_index = pd.factorize(ratings['user_id'])
    ratings['movie_idx'], movie_index = pd.factorize(ratings['movie_id'])
    return ratings, user_index, movie_index

def encode_genres(movies):
    """
    Convert the 'genres' column into multiple binary columns (one-hot encoding).
    For example, if a movie has the genre 'Comedy', the 'Comedy' column will be 1, else 0.
    Returns the updated movies DataFrame with additional genre columns.
    """
    genres_expanded = movies['genres'].str.get_dummies(sep='|')
    movies = pd.concat([movies, genres_expanded], axis=1)
    return movies

def split_data(ratings):
    """
    Split the ratings data into training and test sets.
    Default split ratio is 80% train, 20% test.
    Returns the train and test DataFrames.
    """
    train, test = train_test_split(ratings, test_size=0.2, random_state=42)
    return train, test

def prepare_data():
    """
    Main function which loads data, cleans it, encodes IDs and genres,
    splits the ratings data into train/test sets, and returns all necessary objects.
    """
    ratings, movies = load_movielens_1m()
    ratings, movies = clean_data(ratings, movies)
    ratings, user_index, movie_index = encode_ids(ratings)
    movies = encode_genres(movies)
    train, test = split_data(ratings)
    return train, test, movies, user_index, movie_index

if __name__ == "__main__":
    train, test, movies, user_index, movie_index = prepare_data()
    print("Data is ready!")
    print(f"Train size: {len(train)}, Test size: {len(test)}")