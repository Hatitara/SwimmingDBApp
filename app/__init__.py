from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os

engine = None

def init_app():
    global engine
    app = Flask(__name__)
    app.secret_key = "swimming-secret"

    DB_URL = "mysql+pymysql://root:1234@localhost/swimming?charset=utf8mb4"
    engine = create_engine(DB_URL, echo=False)

    from .routes.swimmer import swimmer_bp
    from .routes.coach import coach_bp
    from .routes.organizer import organizer_bp
    from .routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(swimmer_bp, url_prefix='/swimmer')
    app.register_blueprint(coach_bp, url_prefix='/coach')
    app.register_blueprint(organizer_bp, url_prefix='/organizer')

    return app
