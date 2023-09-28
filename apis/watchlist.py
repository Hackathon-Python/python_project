from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import and_, insert

from utils.adapters import str_to_bool
from database import db
from models.movie import Movie
from models.user import user_movie

watchlist_router = Blueprint("watchlist", __name__)


# convert InstrumentedList of SQLAlchemy objects into JSON
def serialize_movie(movie):
    return {
        "id": movie.id,
        "title": movie.title,
        "description": movie.description,
        "rating": movie.rating,
        "local_rating": movie.local_rating,
        "img_url": movie.img_url
    }


# get the list of user's movies
@watchlist_router.route("/", methods=['GET'])
@login_required
def get_user_watchlist():
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

        if len(user_watchlist) > 0:
            return jsonify([serialize_movie(movie) for movie in user_watchlist]), 200
        else:
            return jsonify({"message": "No movies in watchlist."}), 200

    except Exception as err:
        return jsonify({"error": f"db error: '{err}'"}), 500


# add movie to 'watchlist'
@watchlist_router.route("/", methods=["POST"])
@login_required
def add_to_watchlist():
    try:
        data = request.get_json()
        movie_id = data['movie_id']
        watched = data['watched']

        user = current_user
        movie = Movie.query.get(movie_id)

        if user is None:
            return jsonify({"error": "User is not found"}), 404
        if movie is None:
            return jsonify({"error": "Movie is not found"}), 404

        if movie in user.watchlist:
            query = (user_movie.update().
            where(user_movie.c.user_id == user.id).
            where(user_movie.c.movie_id == movie_id).
            values(
                watched=watched
            ))
        else:
            query = insert(user_movie).values(
                user_id=user.id,
                movie_id=movie_id,
                watched=watched
            )

        db.session.execute(query)
        db.session.commit()

        return jsonify({"message": "Movie added to watchlist."}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# delete movie from watchlist
@watchlist_router.route("/<int:movie_id>", methods=['DELETE'])
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


# change movie status from 'watch later' to 'already watched'
@watchlist_router.route("/<int:movie_id>", methods=["PUT"])
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
