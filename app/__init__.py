from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # ключ для сессий (заменишь на свой позже)
    app.config['SECRET_KEY'] = 'supersecretkey'

    # подключение базы SQLite (users.db в папке data)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../data/users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # инициализация базы
    db.init_app(app)

    # Flask-Login
    login_manager.login_view = 'main.login'   # можешь оставить 'main.welcome'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # регистрация маршрутов
    from . import routes
    app.register_blueprint(routes.bp)

    # создание таблиц
    with app.app_context():
        db.create_all()

    return app