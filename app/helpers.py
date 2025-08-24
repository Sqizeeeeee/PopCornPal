from rapidfuzz import process, fuzz
import pandas as pd
import re
from app import item_cf_model
from .models import Rating

# Загружаем фильмы
movies = pd.read_csv(
    'data/ml-1m/movies.dat',
    sep='::',
    names=['movie_id', 'title', 'genres'],
    engine='python',
    encoding='latin-1'
)

ratings = pd.read_csv(
    'data/ml-1m/ratings.dat',
    sep='::',
    names=['user_id', 'movie_id', 'rating', 'timestamp'],
    engine='python'
)

def clean_title(title):
    title = title.strip()

    # Если год в начале, переносим в конец
    match = re.match(r'^\((\d{4})\)\s*(.*)', title)
    if match:
        title = f"{match.group(2)} ({match.group(1)})"

    # Формат "Lastname, Firstname" -> "Firstname Lastname"
    if ', ' in title:
        parts = title.split(', ')
        if len(parts) == 2:
            title = f"{parts[1]} {parts[0]}"

    # Убираем артикли в начале
    title = re.sub(r'^(the|a|an) ', '', title, flags=re.I)

    # Убираем артикли в конце после запятой
    title = re.sub(r', (the|a|an)$', '', title, flags=re.I)

    # Убираем текст после скобок, который часто мусор
    title = re.sub(r'\s+Institute.*$', '', title, flags=re.I)

    # Первая буква каждого слова заглавная
    title = title.title()

    return title

# Создаём поле для поиска
movies['search_title'] = movies['title'].apply(clean_title)

def search_movies(query, limit=10):
    query_clean = clean_title(query)
    results = []

    for idx, row in movies.iterrows():
        title = row['search_title']
        score1 = fuzz.token_sort_ratio(query_clean, title)
        score2 = fuzz.partial_ratio(query_clean, title)
        score = max(score1, score2)
        results.append((row['movie_id'], row['title'], row['genres'], score))

    results = sorted(results, key=lambda x: x[3], reverse=True)
    matched_movies = []
    for movie_id, title, genres, score in results[:limit]:
        matched_movies.append({
            'id': movie_id,
            'title': title,
            'genres': genres,
            'score': score
        })

    return matched_movies

def format_movie_title(title: str) -> str:
    if ', ' in title:
        parts = title.split(', ')
        if len(parts) == 2:
            return f"{parts[1]} {parts[0]}"
    return title

def extract_year(title):
    match = re.search(r'\((\d{4})\)', title)
    if match:
        year = int(match.group(1))
        clean_title_only = re.sub(r'\s*\(\d{4}\)', '', title)
        return clean_title_only, year
    return title, None

SURVEY_MOVIES = [
    {"id": 356, "title": "Forrest Gump (1994)"},
    {"id": 1721, "title": "Titanic (1997)"},
    {"id": 296, "title": "Pulp Fiction (1994)"},
    {"id": 2953, "title": "Home Alone 2: Lost in New York (1992)"},
    {"id": 3307, "title": "City Lights (1931)"},
    {"id": 2571, "title": "The Matrix (1999)"},
    {"id": 589, "title": "Terminator 2: Judgment Day (1991)"},
    {"id": 364, "title": "The Lion King (1994)"},
    {"id": 2947, "title": "Goldfinger (1964)"}
]

def recommend_movies_for_user(user_id, top_n=5):
    user_rated = ratings[ratings['user_id'] == user_id]['movie_id'].tolist()
    all_movie_ids = movies['movie_id'].tolist()

    predictions = []
    for movie_id in all_movie_ids:
        if movie_id not in user_rated:
            pred_rating = item_cf_model.predict(user_id, movie_id)
            
            # Получаем год фильма
            movie_title = movies.loc[movies['movie_id'] == movie_id, 'title'].values[0]
            _, year = extract_year(movie_title)
            
            # Корректировка слишком высоких рейтингов
            if pred_rating > 4.7:
                if year and year <= 1980:
                    pred_rating = 4.7 + (pred_rating - 4.7) * 0.85
                else:
                    pred_rating = 4.7 + (pred_rating - 4.7) * 0.93

            predictions.append((movie_id, pred_rating))

    # Сортировка по предсказанным рейтингам
    predictions.sort(key=lambda x: x[1], reverse=True)

    top_movies = []
    for movie_id, rating in predictions[:top_n]:
        movie_row = movies.loc[movies['movie_id'] == movie_id]
        if not movie_row.empty:
            title = clean_title(movie_row['title'].values[0])
            top_movies.append({'id': movie_id, 'title': title, 'predicted_rating': round(rating, 2)})

    return top_movies


def recommend_movies_filtered(user_id, genres=None, year_ranges=None, top_n=10):
    """
    Рекомендует фильмы пользователю с учётом фильтров по жанрам и эпохам,
    исключая фильмы, которые пользователь уже оценил в базе.
    
    :param user_id: ID пользователя
    :param genres: список выбранных жанров
    :param year_ranges: список выбранных эпох
    :param top_n: количество фильмов для рекомендации
    :return: список словарей {'id', 'title', 'genres', 'predicted_rating'}
    """
    genres = genres or []
    year_ranges = year_ranges or []

    # Преобразуем выбранные эпохи в интервалы годов
    intervals = []
    for yr in year_ranges:
        if yr == '<=1950':
            intervals.append((None, 1950))
        elif yr == '1950-1970':
            intervals.append((1950, 1970))
        elif yr == '1970-1990':
            intervals.append((1970, 1990))
        elif yr == '>=1990':
            intervals.append((1990, None))

    # Получаем set movie_id уже оценённых пользователем фильмов
    rated_movie_ids = {r.movie_id for r in Rating.query.filter_by(user_id=user_id).all()}

    filtered_movies = []

    for _, row in movies.iterrows():
        movie_id = row['movie_id']
        movie_genres = row['genres'].split('|')
        _, year = extract_year(row['title'])

        # Исключаем фильмы, которые пользователь уже оценил
        if movie_id in rated_movie_ids:
            continue

        # Фильтрация по жанрам
        if genres and not any(g in movie_genres for g in genres):
            continue

        # Фильтрация по выбранным эпохам
        if intervals:
            match_interval = False
            for yf, yt in intervals:
                if ((yf is None or (year and year >= yf)) and
                    (yt is None or (year and year <= yt))):
                    match_interval = True
                    break
            if not match_interval:
                continue

        filtered_movies.append(row)

    # Предсказания рейтингов через item_cf_model
    predictions = []
    for row in filtered_movies:
        movie_id = row['movie_id']
        pred_rating = item_cf_model.predict(user_id, movie_id)

        # Коррекция слишком высоких рейтингов
        _, year = extract_year(row['title'])
        if pred_rating > 4.7:
            if year and year <= 1980:
                pred_rating = 4.7 + (pred_rating - 4.7) * 0.85
            else:
                pred_rating = 4.7 + (pred_rating - 4.7) * 0.93

        predictions.append({
            'id': movie_id,
            'title': clean_title(row['title']),
            'genres': row['genres'],
            'predicted_rating': round(pred_rating, 2)
        })

    # Сортировка по предсказанному рейтингу
    predictions.sort(key=lambda x: x['predicted_rating'], reverse=True)

    return predictions[:top_n]