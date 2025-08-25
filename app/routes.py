from flask import render_template, request, redirect, url_for, flash, jsonify, Blueprint
from flask_login import login_required, login_user, logout_user, current_user
from . import db
from .models import User, Rating
from .helpers import (
    movies, ratings, SURVEY_MOVIES,
    search_movies,
    extract_year,
    recommend_movies_for_user,
    recommend_movies_filtered
)
import re

bp = Blueprint('main', __name__)


# ====== WELCOME / HOME ======
@bp.route('/')
def welcome():
    return render_template('welcome.html')

# ====== REGISTRATION ======
@bp.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash("Username already exists. Try another one", "danger")
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash("Email already registered. Try to log in", "danger")
            return render_template('register.html', email=email)
        if len(password) < 6 or len(password) > 15:
            flash("Password length must be 6-15 characters.", "danger")
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


# ====== LOGIN ======
@bp.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password", "danger")
            return render_template('login.html', email=email)

        login_user(user)
        flash(f"Welcome, {user.username}!", "success")
        return redirect(url_for('main.profile'))

    return render_template('login.html')


# ====== LOGOUT ======
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.login'))


# ====== PROFILE ======
@bp.route('/profile')
@login_required
def profile():
    user = current_user

    # Получаем рекомендации для пользователя
    recommendations = recommend_movies_for_user(user.id, top_n=10)

    # Получаем оценки пользователя (список объектов Rating)
    user_ratings = user.ratings

    return render_template(
        'profile.html',
        user=user,
        ratings=user_ratings,
        recommendations=recommendations
    )


# ====== TOP MOVIES ======
@bp.route('/top-movies')
def top_movies():
    # Форматируем названия и извлекаем год
    movies['title_clean'], movies['year'] = zip(*movies['title'].apply(extract_year))

    # Средние рейтинги
    if ratings.empty:
        top_by_genre = {}
    else:
        movies_stats = ratings.groupby('movie_id')['rating'].mean().reset_index()
        movies_stats = movies_stats.merge(movies[['movie_id', 'title_clean', 'genres', 'year']], on='movie_id')

        top_by_genre = {}
        all_genres = set(g for gs in movies['genres'].str.split('|') for g in gs if g)
        for genre in all_genres:
            genre_movies = movies_stats[movies_stats['genres'].str.contains(genre, na=False)]
            sorted_movies = genre_movies.sort_values('rating', ascending=False)

            new_movies = sorted_movies[sorted_movies['year'] > 1980].head(5)[['title_clean', 'rating', 'year']].values.tolist()
            old_movies = sorted_movies[sorted_movies['year'] <= 1980].head(5)[['title_clean', 'rating', 'year']].values.tolist()
            top_by_genre[genre] = {'new': new_movies, 'old': old_movies}

    return render_template('top_by_genre.html', top_by_genre=top_by_genre)


# ====== RATE MOVIE ======
@bp.route('/rate-movie', methods=['GET', 'POST'])
@login_required
def rate_movie():
    if request.method == 'POST':
        movie_id = request.form.get('movie_id')
        rating_value = request.form.get('rating')

        if not movie_id or not rating_value:
            flash("Movie or rating is missing.", "error")
            return redirect(url_for('main.rate_movie'))

        try:
            movie_id_int = int(movie_id)
            rating_float = float(rating_value)
        except ValueError:
            flash("Invalid movie ID or rating.", "error")
            return redirect(url_for('main.rate_movie'))

        movie_row = movies.loc[movies['movie_id'] == movie_id_int, 'title']
        if movie_row.empty:
            flash("Movie not found.", "error")
            return redirect(url_for('main.rate_movie'))

        movie_title, _ = extract_year(movie_row.values[0])
        existing_rating = Rating.query.filter_by(user_id=current_user.id, movie_id=movie_id_int).first()

        if existing_rating:
            existing_rating.rating = rating_float
            flash(f"Your rating for '{movie_title}' has been updated!", "success")
        else:
            new_rating = Rating(user_id=current_user.id, movie_id=movie_id_int, movie_title=movie_title, rating=rating_float)
            db.session.add(new_rating)
            flash(f"Your rating for '{movie_title}' has been saved!", "success")
        db.session.commit()
        return redirect(url_for('main.rate_movie', q=request.args.get('q', '')))

    query = request.args.get('q', '')
    search_results = search_movies(query) if query else []
    user_ratings = {r.movie_id: r.rating for r in Rating.query.filter_by(user_id=current_user.id).all()} if current_user.is_authenticated else {}

    return render_template('rate_movie.html', query=query, search_results=search_results, user_ratings=user_ratings)


# ====== SURVEY ======
@bp.route('/survey', methods=['GET', 'POST'])
@login_required
def survey():
    if current_user.survey_completed:
        flash("You have already completed the survey.", "info")
        return redirect(url_for('main.profile'))

    if request.method == 'POST':
        data = request.get_json()
        for movie in SURVEY_MOVIES:
            movie_id = str(movie["id"])
            movie_title = movie["title"]
            if movie_id not in data or data[movie_id] == "skip":
                continue
            rating = Rating(user_id=current_user.id, movie_id=int(movie_id), movie_title=movie_title, rating=float(data[movie_id]))
            db.session.add(rating)

        current_user.survey_completed = True
        db.session.commit()
        return jsonify({"message": "Thank you! Your ratings are saved 🎬"})

    return render_template('survey.html', movies=SURVEY_MOVIES)


# ====== SEARCH ======
@bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    genres = []
    year_ranges = []
    recommendations = []
    all_genres = sorted(set(g for m in movies['genres'] for g in m.split('|')))

    if request.method == 'POST':
        genres = request.form.getlist('genres')
        year_ranges = request.form.getlist('year_ranges')
        recommendations = recommend_movies_filtered(user_id=current_user.id, genres=genres, year_ranges=year_ranges, top_n=10)

    return render_template('search.html', all_genres=all_genres, genres=genres, year_ranges=year_ranges, results=recommendations)