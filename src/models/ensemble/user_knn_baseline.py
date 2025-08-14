import numpy as np
import pandas as pd
from collections import defaultdict

class UserKNNBaseline:
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
        users = list(self.user_ratings.keys())
        self.sim_matrix = defaultdict(dict)

        for i, user_i in enumerate(users):
            items_i = self.user_ratings[user_i]
            mean_i = self.user_mean[user_i]
            for j, user_j in enumerate(users):
                if j <= i:
                    continue  # матрица симметричная
                items_j = self.user_ratings[user_j]
                mean_j = self.user_mean[user_j]

                common_items = set(items_i.keys()).intersection(items_j.keys())
                if not common_items:
                    sim = 0
                else:
                    vec_i = np.array([items_i[item] - mean_i for item in common_items])
                    vec_j = np.array([items_j[item] - mean_j for item in common_items])
                    denom = (np.linalg.norm(vec_i) * np.linalg.norm(vec_j))
                    sim = np.dot(vec_i, vec_j) / denom if denom != 0 else 0
                self.sim_matrix[user_i][user_j] = sim
                self.sim_matrix[user_j][user_i] = sim  # симметрия

    def predict(self, user_id, movie_id):
        if user_id not in self.user_ratings:
            return self.global_mean

        neighbors = self.sim_matrix[user_id]
        sims = []
        ratings = []

        for neighbor_id, sim in neighbors.items():
            if movie_id in self.user_ratings[neighbor_id] and neighbor_id != user_id:
                sims.append(sim)
                ratings.append(self.user_ratings[neighbor_id][movie_id] - self.user_mean[neighbor_id])

        if not sims:
            return self.user_mean.get(user_id, self.global_mean)  # fallback

        sims = np.array(sims)
        ratings = np.array(ratings)
        pred = self.user_mean.get(user_id, self.global_mean) + np.dot(sims, ratings) / (np.sum(np.abs(sims)) + 1e-8)
        return np.clip(pred, 1, 5)