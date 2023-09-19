import os
from flask import jsonify
import requests
from database import db
from models.movie import Movie

MOVIE_DB_API_KEY = "b96158f5d67900bd09aee33cc2703106"
API_URL = f"https://api.themoviedb.org/3/tv/top_rated?api_key={MOVIE_DB_API_KEY}"


def populate_movies_from_api():
    response = requests.get(API_URL)
    data = response.json()

    if response.status_code == 200:
        for movie_data in data.get("results", []):
            title = movie_data.get("name", "")
            description = movie_data.get("overview", "")
            rating = movie_data.get("vote_average", "")

            new_movie = Movie(
                title=title,
                description=description,
                rating=rating
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
