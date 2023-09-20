from database import db

from flask_login import UserMixin

user_movie = db.Table("user_movie",
                      db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
                      db.Column("movie_id", db.Integer, db.ForeignKey("movie.id"))
                      )

user_watched_movies = db.Table('user_watched_movies',
                               db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
                               db.Column("movie_id", db.Integer, db.ForeignKey("movie.id"))
                               )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(16), nullable=False)
    watch_later = db.relationship('Movie', secondary=user_movie, backref='watched_by_users')
    already_watched = db.relationship('Movie', secondary=user_watched_movies, backref='already_watched_by_users')
