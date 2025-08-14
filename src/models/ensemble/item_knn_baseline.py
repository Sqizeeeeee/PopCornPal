import numpy as np
import pandas as pd
from collections import defaultdict

class ItemKNNBaseline:
    def __init__(self, k=30):
        self.k = k
        self.global_mean = None
        self.user_mean = None
        self.item_mean = None
        self.user_ratings = None
        self.item_ratings = None
        self.sim_matrix = None

    def fit(self, ratings: pd.DataFrame):
        """
        ratings: pd.DataFrame с колонками ['user_id', 'movie_id', 'rating']
        """
        self.global_mean = ratings['rating'].mean()
        self.user_mean = ratings.groupby('user_id')['rating'].mean().to_dict()
        self.item_mean = ratings.groupby('movie_id')['rating'].mean().to_dict()

        # Формируем словари для быстрого доступа
        self.user_ratings = defaultdict(dict)
        self.item_ratings = defaultdict(dict)
        for row in ratings.itertuples():
            self.user_ratings[row.user_id][row.movie_id] = row.rating
            self.item_ratings[row.movie_id][row.user_id] = row.rating

        # Вычисляем матрицу сходства
        self._compute_similarity()

    def _compute_similarity(self):
        items = list(self.item_ratings.keys())
        self.sim_matrix = defaultdict(dict)

        for i, item_i in enumerate(items):
            users_i = self.item_ratings[item_i]
            mean_i = self.item_mean[item_i]
            for j, item_j in enumerate(items):
                if j <= i:
                    continue  # матрица симметричная
                users_j = self.item_ratings[item_j]
                mean_j = self.item_mean[item_j]

                common_users = set(users_i.keys()).intersection(users_j.keys())
                if not common_users:
                    sim = 0
                else:
                    vec_i = np.array([users_i[u] - mean_i for u in common_users])
                    vec_j = np.array([users_j[u] - mean_j for u in common_users])
                    denom = (np.linalg.norm(vec_i) * np.linalg.norm(vec_j))
                    sim = np.dot(vec_i, vec_j) / denom if denom != 0 else 0
                self.sim_matrix[item_i][item_j] = sim
                self.sim_matrix[item_j][item_i] = sim  # симметрия

    def predict(self, user_id, movie_id):
        if movie_id not in self.item_ratings:
            return self.global_mean
        neighbors = self.sim_matrix[movie_id]
        user_rated_items = self.user_ratings.get(user_id, {})
        sims = []
        ratings = []

        for item_j, sim in neighbors.items():
            if item_j in user_rated_items and item_j != movie_id:
                sims.append(sim)
                ratings.append(user_rated_items[item_j] - self.item_mean[item_j])

        if not sims:
            return self.item_mean.get(movie_id, self.global_mean)  # fallback

        sims = np.array(sims)
        ratings = np.array(ratings)
        pred = self.item_mean.get(movie_id, self.global_mean) + np.dot(sims, ratings) / (np.sum(np.abs(sims)) + 1e-8)
        return np.clip(pred, 1, 5)