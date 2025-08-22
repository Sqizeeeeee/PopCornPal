from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Инициализация расширений
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # 🔑 Ключ для сессий (обязательно замени на свой!)
    app.config['SECRET_KEY'] = 'supersecretkey'

    # 📦 Подключение базы SQLite (лежит в папке data)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../data/users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 🚀 Инициализация базы
    db.init_app(app)

    # 🔐 Flask-Login
    login_manager.login_view = 'main.login'   # куда редиректить неавторизованных
    login_manager.login_message_category = "warning"  # категория flash-сообщения
    login_manager.init_app(app)

    # 📌 Регистрация user_loader
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 🔗 Регистрация маршрутов
    from . import routes
    app.register_blueprint(routes.bp)

    # 🛠 Создание таблиц, если базы ещё нет
    with app.app_context():
        db.create_all()

    return app