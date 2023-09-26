import os
from dotenv import load_dotenv
from flask import jsonify
import requests
from database import db
from models.movie import Movie

load_dotenv()

MOVIE_DB_API_KEY = os.environ.get("MOVIE_DB_API_KEY")
API_URL = os.environ.get("API_URL")
MOVIE_DB_IMAGE_URL = os.environ.get("MOVIE_DB_IMAGE_URL")


def populate_movies_from_api():
    response = requests.get(API_URL)
    data = response.json()

    if response.status_code == 200:
        for movie_data in data.get("results", []):
            title = movie_data.get("name", "")
            description = movie_data.get("overview", "")
            rating = movie_data.get("vote_average", "")
            img_url = movie_data.get("poster_path", "")

            new_movie = Movie(
                title=title,
                description=description,
                rating=rating,
                img_url=f"{MOVIE_DB_IMAGE_URL}/{img_url}",
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
