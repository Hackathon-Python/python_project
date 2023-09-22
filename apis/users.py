from flask import Blueprint, request, jsonify, flash, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import and_

from utils.adapters import str_to_bool
from database import db
from models.movie import Movie
from models.user import User, user_movie
from models.comment import Comment

users_router = Blueprint("users", __name__)


# convert InstrumentedList of SQLAlchemy objects into JSON
def serialize_movie(movie):
    return {
        "id": movie.id,
        "title": movie.title,
        "description": movie.description,
        "rating": movie.rating,
        "img_url": movie.img_url
    }


def serialize_comment(comment):
    return {
        "id": comment.id,
        "text": comment.text,
        "movie_id": comment.movie_id
    }


# sign up
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
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return jsonify({"user_id": new_user.id}), 201
    except Exception as err:
        db.session.rollback()
        return jsonify({"error": f"db error: '{err}'"}), 500


# login
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


# logout
@users_router.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 201


# delete movie from watchlist
@users_router.route("/watchlist/<int:movie_id>", methods=['DELETE'])
@login_required
def delete_from_watchlist(movie_id):
    try:
        user = current_user

        if user:

            relationship = db.session.query(user_movie).filter_by(user_id=user.id, movie_id=movie_id).first()

            if relationship:
                db.session.execute(db.delete(user_movie).filter_by(user_id=user.id, movie_id=movie_id))
                db.session.commit()
                return jsonify({"message": "Movie deleted from watchlist"}), 200
            else:
                return jsonify({"error": "Movie not found in watchlist"}), 404
    except Exception as err:
        return jsonify({"error": f"db error: '{err}'"}), 500


# get the list of user's movies
@users_router.route("/watchlist", methods=['GET'])
@login_required
def get_already_watched():
    try:
        # accept optional watched query param and parse it into bool
        is_watched = str_to_bool(request.args.get("watched"))

        user = current_user

        query = db.session.query(Movie).join(user_movie).filter(
            user_movie.c.user_id == user.id
        )

        if is_watched is not None:
            query = query.filter(and_(user_movie.c.watched == is_watched))

        user_watchlist = query.all()

        return jsonify([serialize_movie(movie) for movie in user_watchlist]), 200
    except Exception as err:
        return jsonify({"error": f"db error: '{err}'"}), 500


# change movie status from 'watch later' to 'already watched'
@users_router.route("/watchlist/<int:movie_id>", methods=["PUT"])
@login_required
def change_movie_status(movie_id):
    try:
        movie = Movie.query.get(movie_id)
        user = current_user

        if not user or not movie:
            return jsonify({"message": "User or movie not found"}), 404

        relationship = db.session.query(user_movie).filter_by(user_id=user.id, movie_id=movie_id).first()

        if relationship:
            is_already_watched = db.session.query(user_movie.c.watched).filter(
                (user_movie.c.user_id == user.id) &
                (user_movie.c.movie_id == movie_id) &
                (user_movie.c.watched == True)  # Check if it's already True
            ).scalar()

            if not is_already_watched:
                update_statement = user_movie.update().where(
                    (user_movie.c.user_id == user.id) &
                    (user_movie.c.movie_id == movie_id)
                ).values(watched=True)

                db.session.execute(update_statement)
                db.session.commit()
            else:
                return jsonify({"message": "The movie is already marked as watched."}), 400

        return jsonify({"message": "Movie is marked as watched."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


# add comment
@users_router.route("/comments", methods=['POST'])
@login_required
def leave_comment():
    try:
        data = request.get_json()
        movie_id = request.args.get("movie_id")

        if "text" not in data or not data["text"].strip():
            return jsonify({"error": "Comment text is missing or empty"}), 400

        text = data["text"]
        movie = Movie.query.get(movie_id)
        user = current_user

        if not user or not movie:
            return jsonify({"message": "User or movie not found"}), 404

        new_comment = Comment(
            text=text
        )

        db.session.add(new_comment)
        user.comments.append(new_comment)
        movie.comments.append(new_comment)
        db.session.commit()

        return jsonify({"message": "Comment is added."}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


# get all user's comments
@users_router.route("/comments", methods=["GET"])
@login_required
def get_user_comments():
    try:
        user = current_user

        if not user:
            return jsonify({"message": "User not found"}), 404

        query = db.session.query(Comment).filter(user.id == Comment.author_id)
        user_comments = query.all()
        db.session.commit()

        if len(user_comments) > 0:
            return jsonify([serialize_comment(comment) for comment in user_comments]), 200
        else:
            return jsonify({"message": "No comments to display"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


# delete comment
@users_router.route("/comments/<int:comment_id>", methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    try:
        user = current_user
        comment = Comment.query.get(comment_id)

        if comment:
            db.session.execute(db.delete(Comment).filter_by(author_id=user.id, id=comment.id))
            db.session.commit()
            return jsonify({"message": "Comment deleted."}), 200
        else:
            return jsonify({"error": "Comment not found."}), 404

        pass
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500
