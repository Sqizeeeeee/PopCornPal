from rapidfuzz import process, fuzz
import pandas as pd
import re
from app import item_cf_model

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