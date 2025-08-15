import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

class UserKNNWithMeans:
    def __init__(self, k=20):
        self.k = k
        self.ratings_matrix = None
        self.user_means = None
        self.global_mean = None

    def fit(self, data: pd.DataFrame):
        """
        data: DataFrame с колонками ['user_id', 'movie_id', 'rating']
        """
        # Строим матрицу рейтингов
        self.ratings_matrix = data.pivot(index='user_id', columns='movie_id', values='rating')
        
        # Средний рейтинг по пользователю
        self.user_means = self.ratings_matrix.mean(axis=1)
        
        # Глобальный средний рейтинг (для новых пользователей/фильмов)
        self.global_mean = data['rating'].mean()
        
        # Заполняем пропуски нулями для вычисления сходства
        self.filled_matrix = self.ratings_matrix.fillna(0)
        
        # Косинусное сходство между пользователями
        self.sim_matrix = pd.DataFrame(
            cosine_similarity(self.filled_matrix),
            index=self.filled_matrix.index,
            columns=self.filled_matrix.index
        )

    def predict(self, user_id, movie_id):
        # Если пользователь или фильм неизвестен
        if user_id not in self.ratings_matrix.index or movie_id not in self.ratings_matrix.columns:
            return self.global_mean

        # Пользователи, у которых есть рейтинг для этого фильма
        users_rated_movie = self.ratings_matrix[movie_id].dropna()
        if users_rated_movie.empty:
            return self.user_means.get(user_id, self.global_mean)

        # Сходство текущего пользователя с другими
        sims = self.sim_matrix.loc[user_id, users_rated_movie.index]

        # Выбираем k ближайших
        top_k = sims.nlargest(self.k)
        ratings = users_rated_movie[top_k.index]

        # Проверка деления на ноль
        if top_k.sum() == 0:
            # Если все сходства нулевые, возвращаем средний рейтинг пользователя или глобальный
            return self.user_means.get(user_id, self.global_mean)

        # Средневзвешенный рейтинг
        pred = np.dot(top_k.values, ratings.values) / top_k.sum()
        
        # Нормируем в диапазон 1–5
        return np.clip(pred, 1, 5)