from rapidfuzz import fuzz
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


def extract_year(title: str):
    """Возвращает (чистое название, год)"""
    title = title.strip()

    # 1. Если год стоит в начале → переносим в конец
    match_start = re.match(r'^\((\d{4})\)\s*(.*)', title)
    if match_start:
        year = int(match_start.group(1))
        title = f"{match_start.group(2)} ({year})"
        return _normalize_title(title), year

    # 2. Ищем год в скобках (обычно в конце)
    match_end = re.search(r'\((\d{4})\)', title)
    if match_end:
        year = int(match_end.group(1))
        clean_title = re.sub(r'\s*\(\d{4}\)', '', title).strip()
        title = f"{clean_title} ({year})"
        return _normalize_title(title), year

    return _normalize_title(title), None


def _normalize_title(title: str) -> str:
    """Форматирует строку — убираем артикли, приводим регистр"""
    # "Lastname, Firstname" -> "Firstname Lastname"
    if ', ' in title:
        parts = title.split(', ')
        if len(parts) == 2:
            title = f"{parts[1]} {parts[0]}"

    # Убираем артикли в начале
    title = re.sub(r'^(the|a|an)\s+', '', title, flags=re.I)

    # Убираем артикли в конце после запятой
    title = re.sub(r',\s*(the|a|an)$', '', title, flags=re.I)

    # Убираем всякий мусор типа "Institute..."
    title = re.sub(r'\s+Institute.*$', '', title, flags=re.I)

    # Title Case
    title = title.title()

    return title


# Создаём поле для поиска
movies['search_title'] = movies['title'].apply(lambda t: extract_year(t)[0])


def search_movies(query, limit=10):
    query_clean, _ = extract_year(query)
    results = []

    for idx, row in movies.iterrows():
        title, _ = extract_year(row['title'])
        score1 = fuzz.token_sort_ratio(query_clean, title)
        score2 = fuzz.partial_ratio(query_clean, title)
        score = max(score1, score2)
        results.append((row['movie_id'], title, row['genres'], score))

    results = sorted(results, key=lambda x: x[3], reverse=True)
    return [
        {'id': mid, 'title': t, 'genres': g, 'score': s}
        for mid, t, g, s in results[:limit]
    ]


def recommend_movies_for_user(user_id, top_n=5):
    user_rated = ratings[ratings['user_id'] == user_id]['movie_id'].tolist()
    all_movie_ids = movies['movie_id'].tolist()

    predictions = []
    for movie_id in all_movie_ids:
        if movie_id not in user_rated:
            pred_rating = item_cf_model.predict(user_id, movie_id)

            # Получаем нормализованный тайтл и год
            movie_title = movies.loc[movies['movie_id'] == movie_id, 'title'].values[0]
            clean_title, year = extract_year(movie_title)

            # Коррекция слишком высоких рейтингов
            if pred_rating > 4.7:
                if year and year <= 1980:
                    pred_rating = 4.7 + (pred_rating - 4.7) * 0.85
                else:
                    pred_rating = 4.7 + (pred_rating - 4.7) * 0.93

            predictions.append((movie_id, clean_title, pred_rating))

    predictions.sort(key=lambda x: x[2], reverse=True)

    return [
        {'id': mid, 'title': t, 'predicted_rating': round(r, 2)}
        for mid, t, r in predictions[:top_n]
    ]


def recommend_movies_filtered(user_id, genres=None, year_ranges=None, top_n=10):
    genres = genres or []
    year_ranges = year_ranges or []

    # Все уникальные жанры
    all_genres = set(g for m in movies['genres'] for g in m.split('|'))

    # Преобразуем выбранные эпохи в интервалы
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

    rated_movie_ids = {r.movie_id for r in Rating.query.filter_by(user_id=user_id).all()}
    filtered_movies = []

    for _, row in movies.iterrows():
        movie_id = row['movie_id']
        clean_title, year = extract_year(row['title'])
        movie_genres = row['genres'].split('|')

        if movie_id in rated_movie_ids:
            continue

        if genres and len(genres) < len(all_genres):
            if not any(g in movie_genres for g in genres):
                continue

        if intervals:
            match_interval = False
            for yf, yt in intervals:
                if ((yf is None or (year and year >= yf)) and
                        (yt is None or (year and year <= yt))):
                    match_interval = True
                    break
            if not match_interval:
                continue

        filtered_movies.append((movie_id, clean_title, row['genres'], year))

    predictions = []
    for movie_id, clean_title, genres_str, year in filtered_movies:
        pred_rating = item_cf_model.predict(user_id, movie_id)

        if pred_rating > 4.7:
            if year and year <= 1980:
                pred_rating = 4.7 + (pred_rating - 4.7) * 0.85
            else:
                pred_rating = 4.7 + (pred_rating - 4.7) * 0.93

        predictions.append({
            'id': movie_id,
            'title': clean_title,
            'genres': genres_str,
            'predicted_rating': round(pred_rating, 2)
        })

    predictions.sort(key=lambda x: x['predicted_rating'], reverse=True)

    return predictions[:top_n]