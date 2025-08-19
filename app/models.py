from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # уникальный ID
    username = db.Column(db.String(80), unique=True, nullable=False)  # имя пользователя
    email = db.Column(db.String(120), unique=True, nullable=False)   # email
    password_hash = db.Column(db.String(128), nullable=False)        # пароль (хэшированный)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)     # дата регистрации

    # метод для установки пароля
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # метод для проверки пароля
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)