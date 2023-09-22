import os
from dotenv import load_dotenv

from flask import Flask, render_template
from flask_login import LoginManager

from database import db
from models.user import User
from models.comment import Comment
from models.movie import Movie

from apis.users import users_router
from apis.movies import movies_router

if os.environ.get("FLASK_ENV") == "development":
    load_dotenv()


def create_app():
    """
    Initializes DB connection, creates an app instance, registers service routers, and returns app instance.

    :return: Flask
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI")
    app.config['DEBUG'] = os.environ.get("DEBUG")
    app.app_context().push()

    # Init DB connection
    db.init_app(app)
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.get_or_404(User, user_id)

    # Register routes
    app.register_blueprint(users_router, url_prefix='/users')
    app.register_blueprint(movies_router, url_prefix='/movies')

    # TODO move me to my own router
    @app.route('/', methods=['GET'])
    def home():
        return render_template("home.html")

    return app


service = create_app()
