from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # уникальный ID
    username = db.Column(db.String(80), unique=True, nullable=False)  # имя пользователя
    email = db.Column(db.String(120), unique=True, nullable=False)   # email
    password_hash = db.Column(db.String(128), nullable=False)        # пароль (хэшированный)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)     # дата регистрации

    ratings = db.relationship('Rating', backref='user', lazy=True)

    # метод для установки пароля
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # метод для проверки пароля
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    movie_id = db.Column(db.Integer)
    movie_title = db.Column(db.String(200))
    rating = db.Column(db.Float)

SURVEY_MOVIES = [
    {"id": 1, "title": "The Matrix (1999)"},
    {"id": 2, "title": "Pulp Fiction (1994)"},
    # TODO: add top 10 films
]