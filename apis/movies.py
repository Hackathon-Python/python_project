from flask import Blueprint, jsonify, request
from sqlalchemy import func
from utils.adapters import remove_special_characters

from database import db
from models.movie import Movie
from models.comment import Comment

movies_router = Blueprint("movies", __name__)


def serialize_comment(comment):
    return {
        "id": comment.id,
        "text": comment.text,
        "author_id": comment.author_id
    }


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
            query = db.session.query(Comment).filter(Comment.movie_id == movie.id)
            movie_comments = query.all()
            db.session.commit()
            if len(movie_comments) > 0:
                return jsonify(movie_data, [serialize_comment(comment) for comment in movie_comments]), 200
            else:
                return jsonify(movie_data, {"message": "No comments to display"}), 200

        else:
            return jsonify({"error": "Movie not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# search for a movie
@movies_router.route("/find", methods=['GET'])
def find_movie():
    movie_input = remove_special_characters(request.args.get("movie_input"))

    try:
        movies = Movie.query.filter(func.lower(Movie.title).like(f"%{movie_input.lower()}%")).all()

        if movies:
            movie_data = [{
                "id": movie.id,
                "title": movie.title,
                "description": movie.description,
                "rating": movie.rating,
                "img_url": movie.img_url} for movie in movies]
            return jsonify(movie_data), 200
        else:
            return jsonify({"error": "Movie is not found"}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
