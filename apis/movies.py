from flask import Blueprint, jsonify, request
from sqlalchemy import func
from flask_login import login_required, current_user
from utils.adapters import remove_special_characters

from database import db
from models.movie import Movie
from models.comment import Comment
from models.user import user_movie

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
                "local_rating": movie.local_rating,
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
                "local_rating": movie.local_rating,
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
                "local_rating": movie.local_rating,
                "img_url": movie.img_url} for movie in movies]
            return jsonify(movie_data), 200
        else:
            return jsonify({"error": "Movie is not found"}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# rate movie and update local_rating with average rating
@movies_router.route("/<int:movie_id>", methods=['GET', 'POST'])
@login_required
def rate_movie(movie_id):
    try:
        data = request.get_json()
        user = current_user
        movie = Movie.query.get(movie_id)
        rating = data["user_rating"]

        if not user or not movie:
            return jsonify({"error": "User or movie not found"}), 404

        if "user_rating" not in data or not data["user_rating"]:
            return jsonify({"error": "Rating is missing or empty"}), 400

        if not isinstance(rating, int) or rating < 1 or rating > 10:
            return jsonify({"error": "Rating must be an integer between 1 and 10"}), 400

        # user can rate movie only if it is watched
        is_already_watched = db.session.query(user_movie.c.watched).filter(
            (user_movie.c.user_id == user.id) &
            (user_movie.c.movie_id == movie_id) &
            (user_movie.c.watched == True)
        ).scalar()

        if not is_already_watched:
            return jsonify({"error": "Movie is not watched yet."}), 400

        db.session.execute(
            user_movie.update().where(
                (user_movie.c.user_id == user.id) &
                (user_movie.c.movie_id == movie_id)
            ).values(user_rating=rating)
        )
        db.session.commit()

        # get all ratings for the movie
        ratings = db.session.query(user_movie.c.user_rating).filter(
            (user_movie.c.movie_id == movie_id) &
            (user_movie.c.user_rating.isnot(None))
        ).all()

        if not ratings:
            return jsonify({"error": "No ratings found for this movie"}), 404

        # calculate average rating
        average_rating = db.session.query(func.avg(user_movie.c.user_rating)).filter(
            (user_movie.c.movie_id == movie_id) &
            (user_movie.c.user_rating.isnot(None))
        ).scalar()

        # update Movie table with average rating
        db.session.execute(
            db.update(Movie)
            .where(Movie.id == movie_id)
            .values(local_rating=average_rating)
        )

        db.session.commit()
        return jsonify({"message": "Rating successfully added.", "average rating": average_rating}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
