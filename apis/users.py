from flask import Blueprint, request, jsonify

from database import db
from models.user import User

users_router = Blueprint("users", __name__)


@users_router.route("/", methods=["POST"])
def create_user():
    # decode request payload as a JSON
    data = request.get_json()

    # validate required fields
    if 'username' not in data:
        return jsonify({'error': 'Missing username'}), 400

    # assemble  new user row
    new_user = User(
        username=data['username'],
        password=data["password"]
    )

    try:
        # write new user data to DB
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"user_id": new_user.id}), 201
    except Exception as err:
        db.session.rollback()
        return jsonify({"error": f"db error: '{err}'"}), 500
