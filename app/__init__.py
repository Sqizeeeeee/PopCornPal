from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # ключ для сессий (заменишь на свой позже)
    app.config['SECRET_KEY'] = 'supersecretkey'

    # подключение базы SQLite (users.db в папке data)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../data/users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # инициализация базы
    db.init_app(app)

    # регистрация маршрутов
    from . import routes
    app.register_blueprint(routes.bp)

    # создание таблиц
    with app.app_context():
        db.create_all()

    return app