import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class ItemBasedCF:
    def __init__(self, ratings: pd.DataFrame, k: int = 25, similarity_threshold: float = 0.1):
        self.ratings = ratings
        self.k = k
        self.similarity_threshold = similarity_threshold
        self.user_item_matrix = None
        self.item_means = None
        self.item_similarity = None

    def fit(self):
        # Create the user-item matrix
        self.user_item_matrix = self.ratings.pivot(index='user_id', columns='movie_id', values='rating')
        
        # Calculate the mean rating for each item (movie)
        self.item_means = self.user_item_matrix.mean(axis=0)
        
        # Center the ratings by subtracting the mean rating of each movie
        self.user_item_matrix = self.user_item_matrix.sub(self.item_means, axis=1).fillna(0)
        
        # Compute cosine similarity between items (across columns)
        similarity = cosine_similarity(self.user_item_matrix.T)
        self.item_similarity = pd.DataFrame(similarity,
                                            index=self.user_item_matrix.columns,
                                            columns=self.user_item_matrix.columns)

    def predict(self, user_id, movie_id):
        if user_id not in self.user_item_matrix.index:
            return self.ratings['rating'].mean()
        
        if movie_id not in self.item_similarity.index:
            # If the movie is not in the matrix, return the average rating
            return self.ratings['rating'].mean()

        # Similarities of the target movie with other movies
        sims = self.item_similarity.loc[movie_id]
        
        # User's ratings on other movies
        user_ratings = self.user_item_matrix.loc[user_id]

        neighbors = []
        for other_movie_id, sim in sims.items():
            if other_movie_id == movie_id or sim < self.similarity_threshold:
                continue
            rating = user_ratings.get(other_movie_id, 0)
            if rating != 0:
                neighbors.append((sim, rating))

        if not neighbors:
            # If no neighbors found, return the average rating of the movie (despite centering)
            return self.item_means.get(movie_id, self.ratings['rating'].mean())

        neighbors.sort(key=lambda x: x[0], reverse=True)
        top_neighbors = neighbors[:self.k]

        sims, ratings = zip(*top_neighbors)
        weighted_avg = np.dot(ratings, sims) / np.sum(sims)

        # Add the average movie rating back (de-normalization)
        pred = self.item_means[movie_id] + weighted_avg
        return min(max(pred, 1), 5)