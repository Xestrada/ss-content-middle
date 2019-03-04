from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pymysql
import os

# Setup App
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS']) # Should change based on is in Development or Production
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS
CORS(app)

# Start Database
db = SQLAlchemy(app)

# Enable Variable Port for Heroku
port = int(os.environ.get('PORT', 33507))

# Import models
from models import Actor
from media_models import Genre
from media_models import Movie, MovieGenre
from media_models import TVShows, TVShowGenre

# Force pymysql to be used as replacement for MySQLdb
pymysql.install_as_MySQLdb()


# [url]/
@app.route('/')
def hello_world():
    return 'Hello World!'


# [url]/actors
@app.route('/actors', methods=['GET'])
def actors():
    actors = Actor.query.order_by().all()
    return jsonify({'actors': [actor.serialize() for actor in actors]})


# Query All Movies in Database
# [url]/movies
@app.route('/movies', methods=['GET'])
def get_movies():
    try:
        movies = Movie.query.all()
        return jsonify({'movies': [movie.serialize() for movie in movies]})
    except Exception as e:
        return str(e)


# Query Movies by Service Provider
# [url]/movies/service=[service_provider]
@app.route('/movies/service=<service>', methods=['GET'])
def get_movies_by_service(service):
    try:
        movies = Movie.query.filter_by(service=service)
        return jsonify({'movies': [movie.serialize() for movie in movies]})
    except Exception as e:
        return str(e)


# Query Movies by Genre Type
# [url]/movies/genre=[genre_type]
@app.route('/movies/genre=<genre>', methods=['GET'])
def get_movies_by_genre(genre):
    try:
        # Determine Singular Genre Object
        genre = Genre.query.filter_by(genre_type=genre).first()

        # Determine all Movie_ids with that Genre
        movie_genre_rel = MovieGenre.query.filter_by(genre_id=genre.id)

        # Create a list of all Movie_ids with that Genre
        movie_ids = list()
        for mgr in movie_genre_rel:
            movie_ids.append(mgr.movie_id)

        # Create a list of all the corresponding Movie objects
        movies = list()
        for id in movie_ids:
            movies.append(Movie.query.filter_by(id=id).first())

        return jsonify({'movies': [movie.serialize() for movie in movies]})
    except Exception as e:
        return str(e)


# Query All TV Shows in Database
# [url]/tv_shows
@app.route('/tv_shows', methods=['GET'])
def get_tv_shows():
    try:
        tv_shows = TVShows.query.all()
        return jsonify({'tv_shows': [tv_show.serialize() for tv_show in tv_shows]})
    except Exception as e:
        return str(e)


# Query TV Shows by Service Provider
# [url]/tv_shows/service=[service_provider]
@app.route('/tv_shows/service=<service>', methods=['GET'])
def get_tv_shows_by_service(service):
    try:
        tv_shows = TVShows.query.filter_by(service=service)
        return jsonify({'tv_shows': [tv_show.serialize() for tv_show in tv_shows]})
    except Exception as e:
        return str(e)


# Query TV Shows by Genre Type
# [url]/tv_shows/genre=[genre_type]
@app.route('/tv_shows/genre=<genre>', methods=['GET'])
def get_tv_shows_by_genre(genre):
    try:
        # Determine Singular Genre Object
        genre = Genre.query.filter_by(genre_type=genre).first()

        # Determine all tvshow_ids with that Genre ID
        tvshow_genre_rel = TVShowGenre.query.filter_by(genre_id=genre.id)

        # Create a list of all TV_Show ids with that Genre
        tvshow_ids = list()
        for tgr in tvshow_genre_rel:
            tvshow_ids.append(tgr.tv_show_id)

        # Create a list of all the corresponding TV_Show objects
        tv_shows = list()
        for id in tvshow_ids:
            tv_shows.append(TVShows.query.filter_by(id=id).first())

        return jsonify({'tv_shows': [tv_show.serialize() for tv_show in tv_shows]})
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run(port=port)
