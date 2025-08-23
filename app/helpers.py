from rapidfuzz import process, fuzz
import pandas as pd
import re

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

# Функция очистки названия для поиска
def clean_title(title):
    title = title.lower().strip()
    # перенос "The X, The" -> "the x"
    title = re.sub(r', (the|a|an)$', '', title)
    # убираем артикли в начале
    title = re.sub(r'^(the|a|an) ', '', title)
    return title

movies['search_title'] = movies['title'].apply(clean_title)


def search_movies(query, limit=10):
    query_clean = clean_title(query)
    results = []

    for idx, row in movies.iterrows():
        title = row['search_title']
        score1 = fuzz.token_sort_ratio(query_clean, title)
        score2 = fuzz.partial_ratio(query_clean, title)
        score = max(score1, score2)  # берём лучший скор
        results.append((row['movie_id'], row['title'], row['genres'], score))

    # Сортируем по скору
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
        clean_title = re.sub(r'\s*\(\d{4}\)', '', title)
        return clean_title, year
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