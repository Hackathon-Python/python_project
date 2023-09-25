from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import and_

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
        "img_url": movie.img_url
    }


# get the list of user's movies
@watchlist_router.route("/", methods=['GET'])
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

        if len(user_watchlist) > 0:
            return jsonify([serialize_movie(movie) for movie in user_watchlist]), 200
        else:
            return jsonify({"message": "No movies in watchlist."}), 200

    except Exception as err:
        return jsonify({"error": f"db error: '{err}'"}), 500


# add movie to 'watch later'
@watchlist_router.route("/watch_later/<int:movie_id>", methods=["POST"])
@login_required
def add_to_watch_later(movie_id):
    try:
        user = current_user
        movie = Movie.query.get(movie_id)

        if user is None:
            return jsonify({"error": "User is not found"}), 404
        if movie is None:
            return jsonify({"error": "Movie is not found"}), 404

        if movie in user.watch_later:
            return jsonify({"message": "Movie is already in watchlist"}), 400

        user.watch_later.append(movie)
        db.session.commit()

        return jsonify({"message": "Movie added to watchlist"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# add movie to 'already watched'
@watchlist_router.route("/already_watched/<int:movie_id>", methods=["POST"])
@login_required
def add_to_already_watched(movie_id):
    try:
        user = current_user
        movie = Movie.query.get(movie_id)

        if user is None:
            return jsonify({"error": "User is not found"}), 404
        if movie is None:
            return jsonify({"error": "Movie is not found"}), 404

        if movie in user.watch_later:
            watched_movie = db.session.query(user_movie).filter_by(user_id=user.id, movie_id=movie.id,
                                                                   watched=True).first()
            if watched_movie:
                return jsonify({"message": "Movie is already watched."}), 400
            else:
                db.session.execute(
                    user_movie.update()
                    .where(user_movie.c.user_id == user.id)
                    .where(user_movie.c.movie_id == movie_id)
                    .values(watched=True)
                )
        elif not movie in user.watch_later:
            user.watch_later.append(movie)
            db.session.execute(
                user_movie.update()
                .where(user_movie.c.user_id == user.id)
                .where(user_movie.c.movie_id == movie_id)
                .values(watched=True)
            )
        db.session.commit()

        return jsonify({"message": "Movie added to already watched movies list."}), 201

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
