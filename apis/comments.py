from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from database import db
from models.movie import Movie
from models.comment import Comment

comments_router = Blueprint("comments", __name__)


def serialize_comment(comment):
    return {
        "id": comment.id,
        "text": comment.text,
        "movie_id": comment.movie_id
    }


# add comment
@comments_router.route("/", methods=['POST'])
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
@comments_router.route("/", methods=["GET"])
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
@comments_router.route("/<int:comment_id>", methods=['DELETE'])
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
