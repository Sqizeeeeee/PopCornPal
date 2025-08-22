from flask import render_template, Blueprint, request, redirect, url_for, flash, session
from functools import wraps
from . import db
from .models import User, Rating, SURVEY_MOVIES
import pandas as pd
import re

bp = Blueprint('main', __name__)

@bp.route('/')
def welcome():
    return render_template('welcome.html')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function



@bp.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash("Username already exists. Try another one", "error")
            return redirect(url_for('main.register'))
        
        if User.query.filter_by(email=email).first():
            flash("Email already registered. Try to log in", "error")
            return render_template('register.html', username=username)
        
        if len(password) < 6:
            flash("Password is too short (min 6 characters).", "danger")
            return render_template('register.html', username=username, email=email)
        
        if len(password) > 15:
            flash("Password is too long (max 15 characters).", "danger")
            return render_template('register.html', username=username, email=email)
        
        if not re.search(r"[A-Z]", password):
            flash("Password must contain at least one uppercase letter.", "danger")
            return render_template('register.html', username=username, email=email)

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can log in now", "success")
        return redirect(url_for('main.login'))
    return render_template('register.html')


@bp.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_or_email = request.form.get('username_or_email')
        password = request.form.get('password')

        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if not user or not user.check_password(password):
            flash("Invalid username, email or password", "error")
            return redirect(url_for('main.login'))
        
        session['user_id'] = user.id
        flash(f'Welcome back, {user.username}!', "success")
        return redirect(url_for('main.profile'))
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out", "info")
    return redirect(url_for('main.welcome'))


@bp.route('/top-movies')
def top_movies():
    import pandas as pd
    import re

    # Загрузка данных
    ratings = pd.read_csv(
        'data/ml-1m/ratings.dat',
        sep='::',
        names=['user_id', 'movie_id', 'rating', 'timestamp'],
        engine='python'
    )
    
    movies = pd.read_csv(
        'data/ml-1m/movies.dat',
        sep='::',
        names=['movie_id', 'title', 'genres'],
        engine='python',
        encoding='latin-1'
    )

    # Исправление названий
    def fix_title(title):
        if ', The' in title:
            return 'The ' + title.replace(', The', '')
        elif ', A' in title:
            return 'A ' + title.replace(', A', '')
        elif ', An' in title:
            return 'An ' + title.replace(', An', '')
        else:
            return title

    movies['title'] = movies['title'].apply(fix_title)

    # Извлечение года
    def extract_year(title):
        match = re.search(r'\((\d{4})\)', title)
        if match:
            year = int(match.group(1))
            clean_title = re.sub(r'\s*\(\d{4}\)', '', title)
            return clean_title, year
        return title, None

    movies[['title', 'year']] = movies['title'].apply(lambda x: pd.Series(extract_year(x)))

    # Средние рейтинги
    movies_stats = ratings.groupby('movie_id')['rating'].mean().reset_index()
    movies_stats = movies_stats.merge(movies, on='movie_id')

    # Формируем топ-5 новых и старых фильмов по жанрам
    top_by_genre = {}
    all_genres = set(g for gs in movies['genres'].str.split('|') for g in gs)

    for genre in all_genres:
        genre_movies = movies_stats[movies_stats['genres'].str.contains(genre)]

        # Сортируем по рейтингу
        sorted_movies = genre_movies.sort_values('rating', ascending=False)

        # Делим на новые и старые
        new_movies = sorted_movies[sorted_movies['year'] > 1980].head(5)[['title', 'rating', 'year']].values.tolist()
        old_movies = sorted_movies[sorted_movies['year'] <= 1980].head(5)[['title', 'rating', 'year']].values.tolist()

        top_by_genre[genre] = {
            'new': new_movies,
            'old': old_movies
        }

    return render_template('top_by_genre.html', top_by_genre=top_by_genre)


@bp.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    user_ratings = user.ratings
    return render_template('profile.html', user=user, ratings=user_ratings)

@bp.route('/survey', methods=['GET'])
@login_required
def survey():
    return render_template('survey.html', movies=SURVEY_MOVIES)
