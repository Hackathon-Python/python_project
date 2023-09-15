import os
from flask import Flask, render_template

from database import db

from apis.users import users_router


def create_app():
    """
    Initializes DB connection, creates an app instance, registers service routers, and returns app instance.

    :return: Flask
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY") or "mysecretkey"
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI") or "sqlite:///python_project.db"
    app.config['DEBUG'] = os.environ.get("DEBUG")
    app.app_context().push()

    # Init DB connection
    db.init_app(app)
    db.create_all()

    # Register routes
    app.register_blueprint(users_router, url_prefix='/users')

    # TODO move me to my own router
    @app.route('/', methods=['GET'])
    def add_user():
        # form = UserForm()  form=form
        return render_template("add_user.html")

    return app


service = create_app()
