import os
from flask import jsonify
import requests
from database import db
from models.movie import Movie

MOVIE_DB_API_KEY = os.environ.get("MOVIE_DB_API_KEY")
API_URL = os.environ.get("API_URL")


def populate_movies_from_api():
    response = requests.get(API_URL)
    data = response.json()

    if response.status_code == 200:
        for movie_data in data.get("results", []):
            title = movie_data.get("name", "")
            description = movie_data.get("overview", "")

            new_movie = Movie(
                title=title,
                description=description,
            )

            try:
                db.session.add(new_movie)
            except Exception as err:
                db.session.rollback()
                print(f"Error inserting data: {err}")

        try:
            db.session.commit()
            print("Database seeding complete.")
        except Exception as err:
            db.session.rollback()
            return jsonify({"error": f"db error: '{err}'"}), 500
    else:
        print("API request failed")
