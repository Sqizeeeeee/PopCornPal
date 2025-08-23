from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(db.Model, UserMixin):   # ✅ Наследуемся от UserMixin
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)  
    username = db.Column(db.String(80), unique=True, nullable=False)  
    email = db.Column(db.String(120), unique=True, nullable=False)   
    password_hash = db.Column(db.String(128), nullable=False)        
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    survey_completed = db.Column(db.Boolean, default=False)     

    ratings = db.relationship('Rating', backref='user', lazy=True)

    # метод для установки пароля
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    # метод для проверки пароля
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Rating(db.Model):
    __tablename__ = "rating"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    movie_id = db.Column(db.Integer)
    movie_title = db.Column(db.String(200))
    rating = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 


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