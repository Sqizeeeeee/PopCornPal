from flask import render_template, Blueprint, request, redirect, url_for, flash, session
from . import db
from .models import User
import pandas as pd

bp = Blueprint('main', __name__)

@bp.route('/')
def welcome():
    return render_template('welcome.html')


@bp.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash("Username already exists. Try another one", "danger")
            return redirect(url_for('main.register'))
        
        if User.query.filter_by(email=email).first():
            flash("Email already registered. Try to log in", "danger")
            return redirect(url_for('main.register'))
        

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
            flash("Invalid username, email or password", "danger")
            return redirect(url_for('main.login'))
        
        session['user_id'] = user.id
        flash(f'Welcome back, {user.username}!', "success")
        return redirect(url_for('main.welcome'))
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out", "info")
    return redirect(url_for('main.welcome'))


@bp.route('/top-movies')
def top_movies():
    import pandas as pd

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

    # Функция для исправления названий
    def fix_title(title):
        if ', The' in title:
            return 'The ' + title.replace(', The', '')
        elif ', A' in title:
            return 'A ' + title.replace(', A', '')
        elif ', An' in title:
            return 'An ' + title.replace(', An', '')
        else:
            return title

    # Применяем исправление
    movies['title'] = movies['title'].apply(fix_title)

    # Считаем средние рейтинги
    movies_stats = ratings.groupby('movie_id')['rating'].mean().reset_index()
    movies_stats = movies_stats.merge(movies, on='movie_id')

    # Формируем топ-10 по жанрам
    top_by_genre = {}
    all_genres = set(g for gs in movies['genres'].str.split('|') for g in gs)

    for genre in all_genres:
        genre_movies = movies_stats[movies_stats['genres'].str.contains(genre)]
        top10 = genre_movies.sort_values('rating', ascending=False).head(10)[['title', 'rating']].values.tolist()
        top_by_genre[genre] = top10

    return render_template('top_by_genre.html', top_by_genre=top_by_genre)