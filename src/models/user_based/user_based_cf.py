import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class UserBasedCF:
    def __init__(self, ratings: pd.DataFrame, k: int = 10, similarity_threshold: float = 0.1):
        """
        User-based Collaborative Filtering.

        Args:
            ratings (pd.DataFrame): DataFrame с колонками ['user_id', 'movie_id', 'rating']
            k (int): число соседей для предсказания
            similarity_threshold (float): минимальное сходство для соседей
        """
        self.ratings = ratings
        self.k = k
        self.similarity_threshold = similarity_threshold
        self.user_item_matrix = None
        self.user_similarity = None

    def fit(self):
        """Строит user-item матрицу и вычисляет сходство между пользователями."""
        self.user_item_matrix = self.ratings.pivot(index='user_id', columns='movie_id', values='rating').fillna(0)
        similarity = cosine_similarity(self.user_item_matrix)
        self.user_similarity = pd.DataFrame(similarity,
                                            index=self.user_item_matrix.index,
                                            columns=self.user_item_matrix.index)

    def predict(self, user_id, movie_id):
        """Предсказывает рейтинг для пользователя и фильма."""
        if user_id not in self.user_item_matrix.index:
            # Пользователь новый — возвращаем глобальный средний рейтинг
            return self.user_item_matrix.values.mean()

        similarities = self.user_similarity.loc[user_id]

        neighbors = []
        for neighbor_id, sim in similarities.items():
            if neighbor_id == user_id:
                continue
            if sim < self.similarity_threshold:
                continue
            if movie_id not in self.user_item_matrix.columns:
                rating = 0
            else:
                rating = self.user_item_matrix.at[neighbor_id, movie_id]
            if rating > 0:
                neighbors.append((sim, rating))

        if not neighbors:
            # Нет подходящих соседей — возвращаем средний рейтинг пользователя или глобальный
            user_ratings = self.user_item_matrix.loc[user_id]
            user_ratings_nonzero = user_ratings[user_ratings > 0]
            if user_ratings_nonzero.empty:
                return self.user_item_matrix.values.mean()
            else:
                return user_ratings_nonzero.mean()

        neighbors.sort(key=lambda x: x[0], reverse=True)
        top_neighbors = neighbors[:self.k]

        sims, ratings = zip(*top_neighbors)
        weighted_avg = np.dot(ratings, sims) / np.sum(sims)
        return weighted_avg

    def recommend(self, user_id: int, n: int = 10):
        """Рекомендует топ-n фильмов пользователю на основе предсказанных рейтингов."""
        if user_id not in self.user_item_matrix.index:
            return []

        rated_movies = self.user_item_matrix.loc[user_id][self.user_item_matrix.loc[user_id] > 0].index
        movies_to_predict = [m for m in self.user_item_matrix.columns if m not in rated_movies]

        predictions = []
        for movie_id in movies_to_predict:
            pred = self.predict(user_id, movie_id)
            predictions.append((movie_id, pred))

        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:n]