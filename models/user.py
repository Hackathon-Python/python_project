from database import db

from flask_login import UserMixin

user_movie = db.Table(
    "user_movie",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("movie_id", db.Integer, db.ForeignKey("movie.id")),
    db.Column("watched", db.Boolean, default=False)
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(16), nullable=False)
    watch_later = db.relationship('Movie', secondary=user_movie, backref='watched_by_users')
    comments = db.relationship("Comment", backref="comment_author")
