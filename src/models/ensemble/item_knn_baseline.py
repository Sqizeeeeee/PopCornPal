import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

class ItemKNNWithMeans:
    def __init__(self, train_data: pd.DataFrame, k=20):
        self.k = k
        self.user_means = None
        self.item_means = None
        self.similarity_matrix = None
        self.ratings_matrix = None
        self.movie_index = None
        self.index_movie = None
        self._fit(train_data)

    def _fit(self, train_data):
        # строим матрицу user-item
        self.ratings_matrix = train_data.pivot_table(index="user_id", columns="movie_id", values="rating")
        self.user_means = self.ratings_matrix.mean(axis=1)
        self.item_means = self.ratings_matrix.mean(axis=0)

        # заменяем NaN на 0 для сходства
        ratings_filled = self.ratings_matrix.fillna(0)
        self.movie_index = {m: i for i, m in enumerate(ratings_filled.columns)}
        self.index_movie = {i: m for m, i in self.movie_index.items()}

        # косинусное сходство между фильмами
        self.similarity_matrix = cosine_similarity(ratings_filled.T)

    def predict(self, user_id, movie_id):
        if movie_id not in self.movie_index:
            return self.user_means.get(user_id, 3.0)

        user_ratings = self.ratings_matrix.loc[user_id]
        user_mean = self.user_means.get(user_id, 3.0)
        target_idx = self.movie_index[movie_id]

        # находим фильмы, которые пользователь оценил
        rated_items = user_ratings.dropna().index
        if len(rated_items) == 0:
            return self.item_means.get(movie_id, 3.0)

        similarities = []
        ratings_diff = []
        for m in rated_items:
            idx = self.movie_index[m]
            sim = self.similarity_matrix[target_idx, idx]
            if sim > 0:
                similarities.append(sim)
                ratings_diff.append(user_ratings[m] - self.item_means[m])

        if len(similarities) == 0:
            return self.item_means.get(movie_id, 3.0)

        # формула "WithMeans"
        pred = self.item_means[movie_id] + np.dot(similarities, ratings_diff) / np.sum(similarities)
        return np.clip(pred, 1, 5)