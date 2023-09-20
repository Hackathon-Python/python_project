from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from database import db
from models.movie import Movie
from models.user import User

movies_router = Blueprint("movies", __name__)


# get all movies
@movies_router.route("/", methods=['GET'])
def get_all_movies():
    try:
        all_movies = Movie.query.all()

        movies_data = []

        for movie in all_movies:
            movie_data = {
                "id": movie.id,
                "title": movie.title,
                "description": movie.description,
                "rating": movie.rating,
                "img_url": movie.img_url
            }
            movies_data.append(movie_data)

        return jsonify(movies_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# get single movie
@movies_router.route("/<int:movie_id>", methods=['GET'])
def get_single_movie(movie_id):
    try:
        movie = Movie.query.get(movie_id)

        if movie:
            movie_data = {
                "id": movie.id,
                "title": movie.title,
                "description": movie.description,
                "rating": movie.rating,
                "img_url": movie.img_url

            }
            return jsonify(movie_data), 200
        else:
            return jsonify({"error": "Movie not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# add movie to watchlist
@movies_router.route("/add_to_watchlist", methods=["POST"])
@login_required
def add_to_watch_later():
    try:
        user_id = request.args.get("user_id")
        movie_id = request.args.get("movie_id")

        user = User.query.get(user_id)
        movie = Movie.query.get(movie_id)

        if user is None:
            return jsonify({"error": "User is not found"}), 404
        if movie is None:
            return jsonify({"error": "Movie is not found"}), 404

        if movie in current_user.watch_later:
            return jsonify({"message": "Movie is already in watchlist"}), 200

        user.watch_later.append(movie)
        db.session.commit()

        return jsonify({"message": "Movie added to watchlist"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
