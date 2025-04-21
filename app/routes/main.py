from flask import Blueprint, render_template
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app import engine
from flask import jsonify


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('home.html')

@main_bp.route("/test-db")
def test_db_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1;")).scalar_one()
            conn.commit()
            return jsonify({"result": result})
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500