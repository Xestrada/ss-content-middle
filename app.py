from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pymysql
import os

# Setup App
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS']) #Should change based on is in Development or Production
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS
CORS(app)

# Start Database
db = SQLAlchemy(app)

# Enable Variable port for Heroku
port = int(os.environ.get('PORT', 33507))

# Import models
from models import Actor
from media_models import Genre
from media_models import Movie, MovieGenre
from media_models import TVShows

# Force pymysql to be used as replacement for MySQLdb
pymysql.install_as_MySQLdb()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/actors', methods=['GET'])
def actors():
    actors = Actor.query.order_by().all()
    return jsonify({'actors': [actor.serialize() for actor in actors]})


# Routes Regarding Movies
@app.route('/movies', methods=['GET'])
def get_movies():
    try:
        movies = Movie.query.all()
        return jsonify({'movies': [movie.serialize() for movie in movies]})
    except Exception as e:
        return str(e)


@app.route('/movies/service=<service>', methods=['GET'])
def get_movies_by_service(service):
    try:
        movies = Movie.query.filter_by(service=service)
        return jsonify({'movies': [movie.serialize() for movie in movies]})
    except Exception as e:
        return str(e)


@app.route('/movies/genre=<genre>', methods=['GET'])
def get_movies_by_genre(genre):
    try:
        # Determine Singular Genre Object
        genre = Genre.query.filter_by(genre_type=genre).first()

        # Determine all Movie_ids with that Genre
        movie_genre_rel = MovieGenre.query.filter_by(genre_id=genre.id)
        # Get all Movie ids with that Genre
        movie_ids = list()
        for mgr in movie_genre_rel:
            movie_ids.append(mgr.movie_id)

        # Get all Movie objects
        movies = list()
        for id in movie_ids:
            movies.append(Movie.query.filter_by(id=id).first())

        return jsonify({'movies': [movie.serialize() for movie in movies]})
    except Exception as e:
        return str(e)


# Routes Regarding TV-Shows
@app.route('/tv_shows', methods=['GET'])
def get_tv_shows():
    try:
        tv_shows = TVShows.query.all()
        return jsonify({'tv_shows': [tv_show.serialize() for tv_show in tv_shows]})
    except Exception as e:
        return str(e)


@app.route('/tv_shows/service=<service>', methods=['GET'])
def get_tv_shows_by_service(service):
    try:
        tv_shows = TVShows.query.filter_by(service=service)
        return jsonify({'tv_shows': [tv_show.serialize() for tv_show in tv_shows]})
    except Exception as e:
        return str(e)


# @app.route('/tv_shows/genre=<genre>', methods=['GET'])
# def get_tv_shows_by_genre(genre):
#     try:
#         tv_shows = TV_Shows.query.filter_by(genre=genre)
#         return jsonify({'tv_shows': [tv_show.serialize() for tv_show in tv_shows]})
#     except Exception as e:
#         return str(e)


if __name__ == '__main__':
    app.run(port=port)
