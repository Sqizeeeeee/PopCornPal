import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class UserBasedCF:
    def __init__(self, ratings: pd.DataFrame, k: int = 10, similarity_threshold: float = 0.1):
        """
        User-based Collaborative Filtering.

        Args:
            ratings (pd.DataFrame): DataFrame with columns ['user_id', 'movie_id', 'rating']
            k (int): number of neighbors to consider for prediction
            similarity_threshold (float): minimum similarity threshold for neighbors
        """
        self.ratings = ratings
        self.k = k
        self.similarity_threshold = similarity_threshold
        self.user_item_matrix = None
        self.user_similarity = None

    def fit(self):
        """Builds the user-item matrix and computes user-user similarity matrix."""
        # Create user-item rating matrix, fill missing values with 0
        self.user_item_matrix = self.ratings.pivot(index='user_id', columns='movie_id', values='rating').fillna(0)
        
        # Compute cosine similarity between all users
        similarity = cosine_similarity(self.user_item_matrix)

        # Store similarity in a DataFrame with user ids as indices and columns
        self.user_similarity = pd.DataFrame(similarity,
                                            index=self.user_item_matrix.index,
                                            columns=self.user_item_matrix.index)

    def predict(self, user_id, movie_id):
        """Predicts rating for a given user and movie."""
        if user_id not in self.user_item_matrix.index:
            # If user is new (not in training data), return global average rating
            return self.user_item_matrix.values.mean()

        # Get similarities between the user and all other users
        similarities = self.user_similarity.loc[user_id]

        neighbors = []
        # Iterate over neighbors (other users)
        for neighbor_id, sim in similarities.items():
            if neighbor_id == user_id:
                continue  # skip self
            if sim < self.similarity_threshold:
                continue  # skip neighbors with low similarity
            # Check if the neighbor has rated the movie
            if movie_id not in self.user_item_matrix.columns:
                rating = 0
            else:
                rating = self.user_item_matrix.at[neighbor_id, movie_id]
            if rating > 0:
                # Include neighbors that have rated the movie
                neighbors.append((sim, rating))

        if not neighbors:
            # No suitable neighbors found
            # Return user average rating if available, otherwise global average
            user_ratings = self.user_item_matrix.loc[user_id]
            user_ratings_nonzero = user_ratings[user_ratings > 0]
            if user_ratings_nonzero.empty:
                return self.user_item_matrix.values.mean()
            else:
                return user_ratings_nonzero.mean()

        # Sort neighbors by similarity in descending order
        neighbors.sort(key=lambda x: x[0], reverse=True)

        # Take top k neighbors
        top_neighbors = neighbors[:self.k]

        sims, ratings = zip(*top_neighbors)
        # Calculate weighted average rating based on neighbors' ratings and similarities
        weighted_avg = np.dot(ratings, sims) / np.sum(sims)
        return weighted_avg

    def recommend(self, user_id: int, n: int = 10):
        """Recommends top-n movies for a user based on predicted ratings."""
        # If user is new, return empty list of recommendations
        if user_id not in self.user_item_matrix.index:
            return []

        # Find movies that the user has already rated
        rated_movies = self.user_item_matrix.loc[user_id][self.user_item_matrix.loc[user_id] > 0].index
        
        # Consider only movies that the user hasn't rated yet
        movies_to_predict = [m for m in self.user_item_matrix.columns if m not in rated_movies]

        predictions = []
        # Predict rating for each unrated movie
        for movie_id in movies_to_predict:
            pred = self.predict(user_id, movie_id)
            predictions.append((movie_id, pred))

        # Sort movies by predicted rating in descending order
        predictions.sort(key=lambda x: x[1], reverse=True)

        # Return top-n recommendations
        return predictions[:n]