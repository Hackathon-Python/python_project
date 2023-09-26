# MovieHub API

## Description:

This Python project is a web application that allows users to interact with a movie database.
Users can perform various actions such as signing up, logging in, searching for movies, rating movies, adding movies to
their watchlist, leaving comments on movies, and more.

To seed the database with top-rated TV shows, I use data from [The Movie Database (TMDb)](https://www.themoviedb.org/).
You can find the API endpoint at the following
URL: [API_URL](https://api.themoviedb.org/3/tv/top_rated?api_key=YOUR_API_KEY)
Make sure to replace `YOUR_API_KEY` with your actual API key if it's required to access the data.

## Key Features:

- __User Authentication__: Users can sign up and log in to the application.
- __Movie Management__: Users can search for movies, view movie details, and rate movies.
- __Watchlist__: Users can add movies to their watchlist and mark them as watched.
- __Comments__: Users can leave comments on movies.
- __Rating System__: The application calculates and displays average ratings for each movie.
- __Database Interaction__: The project uses SQLAlchemy to interact with the database.

## Technologies:

- [Python](https://www.python.org/)
- [Flask](https://flask.palletsprojects.com/en/2.3.x/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/)

## Installation

### `pip install -r requirements.txt` - install dependencies

## Development

### `make run` - set up development environment

### `make build` - create application build