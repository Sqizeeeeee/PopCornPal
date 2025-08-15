import pandas as pd
from data_loader import load_movielens_1m

def main():
    # Load the MovieLens 1M dataset, obtaining ratings and movies dataframes
    ratings, movies = load_movielens_1m()
    
    # Print the total number of unique users in the ratings dataset
    # Print the total number of unique movies in the ratings dataset
    # Print the total number of ratings given
    print(f"All users: {ratings['user_id'].nunique()}")
    print(f"All films: {ratings['movie_id'].nunique()}")
    print(f"All ratings: {len(ratings)}\n")

    # Display the distribution of rating values (how many times each rating appears)
    print("Dictribution of ratings:")
    print(ratings['rating'].value_counts().sort_index())
    
    # Calculate the number of ratings given by each user
    # Calculate the number of ratings received by each movie
    ratings_per_user = ratings.groupby('user_id').size()
    ratings_per_movie = ratings.groupby('movie_id').size()
    
    # Calculate and print the average number of ratings per user
    # Calculate and print the average number of ratings per movie
    print(f'\nAverage ratings per user: {ratings_per_user.mean():.2f}')
    print(f'\nAverage ratings per film: {ratings_per_movie.mean():.2f}\n')
    
    # Show top 5 users who have given the most ratings
    # Show top 5 movies that have received the most ratings
    print("top-5 active users:")
    print(ratings_per_user.sort_values(ascending=False).head())
    
    print("\ntop-5 popular films:")
    print(ratings_per_movie.sort_values(ascending=False).head())
    
    # Split movie genres by '|' and explode to get a series of individual genres
    # Print frequency count of each genre across all movies
    genres_series = movies['genres'].str.split('|').explode()
    print("\nfrequency of genres:")
    print(genres_series.value_counts())

if __name__ == "__main__":
    main()