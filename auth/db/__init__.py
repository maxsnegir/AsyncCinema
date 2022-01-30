from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from settings import PostgresSettings

db = SQLAlchemy()
migrate = Migrate()


def init_db(app: Flask):
    app.config['SQLALCHEMY_DATABASE_URI'] = PostgresSettings().DSN
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)
