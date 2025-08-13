import numpy as np
import pandas as pd

class MatrixFactorization:
    def __init__(self, ratings, n_factors=20, n_epochs=20, lr=0.01, reg=0.1):
        self.ratings = ratings
        self.n_factors = n_factors
        self.n_epochs = n_epochs
        self.lr = lr
        self.reg = reg
        self.user_factors = None
        self.item_factors = None
        self.user_bias = None
        self.item_bias = None
        self.global_mean = None
        self.user_mapping = None
        self.item_mapping = None

    def fit(self):
        users = self.ratings['user_id'].unique()
        items = self.ratings['movie_id'].unique()

        self.user_mapping = {u: i for i, u in enumerate(users)}
        self.item_mapping = {i: j for j, i in enumerate(items)}

        n_users = len(users)
        n_items = len(items)

        self.user_factors = np.random.normal(scale=0.1, size=(n_users, self.n_factors))
        self.item_factors = np.random.normal(scale=0.1, size=(n_items, self.n_factors))
        self.user_bias = np.zeros(n_users)
        self.item_bias = np.zeros(n_items)
        self.global_mean = self.ratings['rating'].mean()

        for epoch in range(self.n_epochs):
            for row in self.ratings.itertuples():
                u = self.user_mapping[row.user_id]
                i = self.item_mapping[row.movie_id]
                rating = row.rating

                pred = self.predict_single(u, i)
                err = rating - pred

                self.user_bias[u] += self.lr * (err - self.reg * self.user_bias[u])
                self.item_bias[i] += self.lr * (err - self.reg * self.item_bias[i])

                user_f = self.user_factors[u]
                item_f = self.item_factors[i]

                self.user_factors[u] += self.lr * (err * item_f - self.reg * user_f)
                self.item_factors[i] += self.lr * (err * user_f - self.reg * item_f)

            # Можно вывести ошибку по эпохе для контроля (опционально)

    def predict_single(self, u, i):
        pred = self.global_mean + self.user_bias[u] + self.item_bias[i] + self.user_factors[u].dot(self.item_factors[i])
        return np.clip(pred, 1, 5)

    def predict(self, user_id, movie_id):
        if user_id not in self.user_mapping or movie_id not in self.item_mapping:
            return self.global_mean
        u = self.user_mapping[user_id]
        i = self.item_mapping[movie_id]
        return self.predict_single(u, i)