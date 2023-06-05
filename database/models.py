from datetime import date
from dotenv import load_dotenv
from flask_migrate import Migrate
from sqlalchemy import Column, String, Integer, ForeignKey, Float, Date
from flask_sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


# Get track modification from the environment variable
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS') == 'True'

# Get the database URL from the environment variable
database_path = os.environ.get('DATABASE_URL')

db = SQLAlchemy()

# ----------------------------------------------------------------------------#


def setup_db(app):
    """binds a flask application and a SQLAlchemy service"""
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
    # postgresql://postgres_deployment_example_u65m_user:c9uJmtgQVhSz6tlHdMHTd8vdGW69wuUO@dpg-chitteu4dad01ah3t3u0-a.singapore-postgres.render.com/postgres_deployment_example_u65m
    migrate = Migrate(app, db)
    db.app = app
    db.init_app(app)


def db_drop_and_create_all():
    """
    drops the database tables and starts fresh
    can be used to initialize a clean database
    """
    db.drop_all()
    db.create_all()


class ActorInMovie(db.Model):
    __tablename__ = "actor_in_movie"

    movie_id = Column(Integer, ForeignKey("movies.id"), primary_key=True)
    actor_id = Column(Integer, ForeignKey("actors.id"), primary_key=True)

    def __init__(self, movie_id: int, actor_id: int):
        self.movie_id = movie_id
        self.actor_id = actor_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    @property
    def short_info(self):
        return {
            "movie_id": self.movie_id,
            "actor_id": self.actor_id
        }

    @property
    def long_info(self):
        return {
            "movie_id": self.movie_id,
            "actor_id": self.actor_id
        }

    @property
    def full_info(self):
        return {
            "movie_id": self.movie_id,
            "actor_id": self.actor_id
        }

    def __repr__(self):
        return "<ActorInMovie(movie_id={}, actor_id={})>".format(
            self.movie_id, self.actor_id)


class Movie(db.Model):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String(256), nullable=False)
    release_year = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)
    imdb_rating = Column(Float, nullable=False)
    cast = db.relationship(
        'ActorInMovie', backref='movies', lazy='joined', cascade="all, delete")

    def __init__(self, title: str, release_year: int, duration: int, imdb_rating: float):
        self.title = title
        self.release_year = release_year
        self.duration = duration
        self.imdb_rating = imdb_rating

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    @property
    def short_info(self):
        return {
            "id": self.id,
            "title": self.title,
            "release_year": self.release_year
        }

    @property
    def long_info(self):
        return {
            "title": self.title,
            "duration": self.duration,
            "release_year": self.release_year,
            "imdb_rating": self.imdb_rating
        }

    @property
    def full_info(self):
        return {
            "title": self.title,
            "duration": self.duration,
            "release_year": self.release_year,
            "imdb_rating": self.imdb_rating,
            "cast": [actor.actors.name for actor in self.cast]
        }

    def __repr__(self):
        return "<Movie(title='{}', release_year={}, imdb_rating={}, duration={})>".format(
            self.title, self.release_year, self.imdb_rating, self.duration)


class Actor(db.Model):
    __tablename__ = "actors"

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    full_name = Column(String(512), nullable=False, default='')
    date_of_birth = Column(Date, nullable=False)
    movies = db.relationship(
        'ActorInMovie', backref='actors', lazy='joined', cascade="all, delete")

    def __init__(self, name: str, full_name: str, date_of_birth: date):
        self.name = name
        self.full_name = full_name
        self.date_of_birth = date_of_birth

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    @property
    def short_info(self):
        return {
            "id": self.id,
            "name": self.name
        }

    @property
    def long_info(self):
        return {
            "name": self.name,
            "full_name": self.full_name,
            "date_of_birth": self.date_of_birth.strftime("%B %d, %Y")
        }

    @property
    def full_info(self):
        print(self.movies)
        return {
            "name": self.name,
            "full_name": self.full_name,
            "date_of_birth": self.date_of_birth.strftime("%B %d, %Y"),
            "movies": [movie.movies.title for movie in self.movies]
        }

    def __repr__(self):
        return "<Actor(name='{}', full_name='{}', date_of_birth={})>".format(
            self.name, self.full_name, self.date_of_birth)
