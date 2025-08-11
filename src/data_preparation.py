import pandas as pd
from sklearn.model_selection import train_test_split
from data_loader import load_movielens_1m

def clean_data(ratings, movies):
    """
    Удаляет дубликаты и пропуски из данных.
    Возвращает очищенные таблицы ratings и movies.
    """
    ratings = ratings.drop_duplicates()
    movies = movies.drop_duplicates()

    if ratings.isnull().any().any():
        ratings = ratings.dropna()
    if movies.isnull().any().any():
        movies = movies.dropna()

    return ratings, movies

def encode_ids(ratings):
    """
    Преобразует user_id и movie_id в числовые индексы user_idx и movie_idx.
    Это нужно, чтобы модель могла работать с числовыми идентификаторами.
    Возвращает обновленный ratings и объекты с оригинальными индексами.
    """
    ratings['user_idx'], user_index = pd.factorize(ratings['user_id'])
    ratings['movie_idx'], movie_index = pd.factorize(ratings['movie_id'])
    return ratings, user_index, movie_index

def encode_genres(movies):
    """
    Преобразует колонку genres в несколько бинарных колонок (one-hot encoding).
    Например, если жанр Comedy есть, то в колонке 'Comedy' будет 1, иначе 0.
    Возвращает обновленный movies с дополнительными колонками жанров.
    """
    genres_expanded = movies['genres'].str.get_dummies(sep='|')
    movies = pd.concat([movies, genres_expanded], axis=1)
    return movies

def split_data(ratings):
    """
    Разбивает данные рейтингов на тренировочную и тестовую выборки.
    Стандартное соотношение 80/20.
    Возвращает две таблицы: train и test.
    """
    train, test = train_test_split(ratings, test_size=0.2, random_state=42)
    return train, test

def prepare_data():
    """
    main fucnction which downloads data, divide data into test/train and returns all objects
    """
    ratings, movies = load_movielens_1m()
    ratings, movies = clean_data(ratings, movies)
    ratings, user_index, movie_index = encode_ids(ratings)
    movies = encode_genres(movies)
    train, test = split_data(ratings)
    return train, test, movies, user_index, movie_index

if __name__ == "__main__":
    train, test, movies, user_index, movie_index = prepare_data()
    print("Data is ready!")
    print(f"Train size: {len(train)}, Test size: {len(test)}")