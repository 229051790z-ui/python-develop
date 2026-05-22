from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db
from auth import auth_bp
from books import books_bp
from borrow import borrow_bp
from users import users_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(borrow_bp)
    app.register_blueprint(users_bp)

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
