import pandas as pd
from data_loader import load_movielens_1m

def main():
    ratings, movies = load_movielens_1m()
    
    print(f"All users: {ratings['user_id'].nunique()}")
    print(f"All films: {ratings['movie_id'].nunique()}")
    print(f"All ratings: {len(ratings)}\n")
    
    print("Dictribution of ratings:")
    print(ratings['rating'].value_counts().sort_index())
    
    ratings_per_user = ratings.groupby('user_id').size()
    ratings_per_movie = ratings.groupby('movie_id').size()
    
    print(f'\nAverage ratings per user: {ratings_per_user.mean():.2f}')
    print(f'\nAverage ratings per film: {ratings_per_movie.mean():.2f}\n')
    
    print("top-5 active users:")
    print(ratings_per_user.sort_values(ascending=False).head())
    
    print("\ntop-5 popular films:")
    print(ratings_per_movie.sort_values(ascending=False).head())
    
    genres_series = movies['genres'].str.split('|').explode()
    print("\nfrequency of genres:")
    print(genres_series.value_counts())

if __name__ == "__main__":
    main()