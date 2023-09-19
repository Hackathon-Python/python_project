from flask import Blueprint, jsonify, request

from database import db
from models.movie import Movie

movies_router = Blueprint("movies", __name__)


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


@movies_router.route("/delete", methods=["DELETE"])
def delete_movie():
    try:
        movie_id = request.args.get("id")
        movie = db.get_or_404(Movie, movie_id)

        db.session.delete(movie)
        db.session.commit()
        return jsonify({"Successfully deleted movie_id": movie.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
