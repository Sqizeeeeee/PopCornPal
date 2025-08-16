import numpy as np
import pandas as pd

class MatrixFactorization:
    def __init__(self, ratings, n_factors=20, n_epochs=20, lr=0.01, reg=0.1):
        # Initialize the model with ratings data and hyperparameters
        self.ratings = ratings                  # DataFrame with columns: user_id, movie_id, rating
        self.n_factors = n_factors              # Number of latent factors
        self.n_epochs = n_epochs                # Number of training epochs
        self.lr = lr                          # Learning rate
        self.reg = reg                        # Regularization term to avoid overfitting
        
        # Placeholders for learned parameters
        self.user_factors = None               # Latent factors for users
        self.item_factors = None               # Latent factors for items (movies)
        self.user_bias = None                   # Bias terms for users
        self.item_bias = None                   # Bias terms for items
        self.global_mean = None                 # Global average rating
        self.user_mapping = None                # Maps user IDs to indices
        self.item_mapping = None                # Maps movie IDs to indices

    def fit(self):
        # Extract unique users and items from the ratings dataset
        users = self.ratings['user_id'].unique()
        items = self.ratings['movie_id'].unique()

        # Create mappings from user/item IDs to matrix indices
        self.user_mapping = {u: i for i, u in enumerate(users)}
        self.item_mapping = {i: j for j, i in enumerate(items)}

        n_users = len(users)
        n_items = len(items)

        # Initialize user and item latent factor matrices with small random values
        self.user_factors = np.random.normal(scale=0.1, size=(n_users, self.n_factors))
        self.item_factors = np.random.normal(scale=0.1, size=(n_items, self.n_factors))
        
        # Initialize user and item biases to zero
        self.user_bias = np.zeros(n_users)
        self.item_bias = np.zeros(n_items)
        
        # Calculate the global mean rating to use as a baseline
        self.global_mean = self.ratings['rating'].mean()

        # Training loop over epochs
        for epoch in range(self.n_epochs):
            # Iterate through each rating in the dataset
            for row in self.ratings.itertuples():
                # Map user and item IDs to their indices
                u = self.user_mapping[row.user_id]
                i = self.item_mapping[row.movie_id]
                rating = row.rating

                # Predict the current rating and calculate the error
                pred = self.predict_single(u, i)
                err = rating - pred

                # Update user and item bias terms using gradient descent
                self.user_bias[u] += self.lr * (err - self.reg * self.user_bias[u])
                self.item_bias[i] += self.lr * (err - self.reg * self.item_bias[i])

                user_f = self.user_factors[u]
                item_f = self.item_factors[i]

                # Update latent factors with gradient descent, regularized by reg parameter
                self.user_factors[u] += self.lr * (err * item_f - self.reg * user_f)
                self.item_factors[i] += self.lr * (err * user_f - self.reg * item_f)

    def predict_single(self, u, i):
        # Predict the rating for a single user-item pair using biases and dot product of factors
        pred = self.global_mean + self.user_bias[u] + self.item_bias[i] + self.user_factors[u].dot(self.item_factors[i])
        # Clip the prediction to the valid rating range [1, 5]
        return np.clip(pred, 1, 5)

    def predict(self, user_id, movie_id):
        # Predict rating for given user_id and movie_id
        # If user or item is unknown, return global mean rating
        if user_id not in self.user_mapping or movie_id not in self.item_mapping:
            return self.global_mean
        
        u = self.user_mapping[user_id]
        i = self.item_mapping[movie_id]
        return self.predict_single(u, i)