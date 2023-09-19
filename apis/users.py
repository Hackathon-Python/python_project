from flask import Blueprint, request, jsonify, flash, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user

from database import db
from models.user import User

users_router = Blueprint("users", __name__)


@users_router.route("/signup", methods=['POST'])
def create_user():
    data = request.get_json()
    username = data['username']
    password = data['password']

    result = db.session.execute(db.select(User).where(User.username == username))
    user = result.scalar()

    if user:
        flash("You've already signed up with that email, log in instead!")

    if username is None or username.strip() == "":
        flash("Username cannot be empty.", category="error")
        response = make_response("Bad Request: Username cannot be empty", 400)
        return response

    if password is None or password.strip() == "":
        flash("Password cannot be empty.", category="error")
        response = make_response("Bad Request: Password cannot be empty", 400)
        return response

    hash_and_salted_password = generate_password_hash(
        password,
        method='pbkdf2:sha256',
        salt_length=8
    )

    # assemble  new user row
    new_user = User(
        username=username,
        password=hash_and_salted_password
    )

    try:
        # write new user data to DB
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return jsonify({"user_id": new_user.id}), 201
    except Exception as err:
        db.session.rollback()
        return jsonify({"error": f"db error: '{err}'"}), 500


@users_router.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    try:
        result = db.session.execute(db.select(User).where(User.username == username))
        user = result.scalar()

        if not user:
            flash("That username does not exist, please try again.", category="error")
            response = make_response("Bad Request: Username does not exist", 400)
            return response
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.', category="error")
            response = make_response("Bad Request: Password incorrect", 400)
            return response
        else:
            login_user(user)
            return jsonify({"User user_id is logged in": user.id}), 201
    except Exception as err:
        return jsonify({"error": f"db error: '{err}'"}), 500


@users_router.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 201
