from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pymysql
import os
import datetime

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
def get_actors():
    actors = Actor.query.order_by().all()
    return jsonify({'actors': [actor.serialize() for actor in actors]})


# [url]/actors/fn=[first_name]
@app.route('/actors/fn=<first_name>', methods=['GET'])
def get_actors_by_first_name(first_name):
    query_name = "{}%".format(first_name)
    actors = Actor.query.filter(Actor.first_name.like(query_name)).all()
    return jsonify({'actors': [actor.serialize() for actor in actors]})


# [url]/actors/ln=[last_name]
@app.route('/actors/ln=<last_name>', methods = ['GET'])
def get_actors_by_last_name(last_name):
    query_name = "{}%".format(last_name)
    actors = Actor.query.filter(Actor.last_name.like(query_name)).all()
    return jsonify({'actors': [actor.serialize() for actor in actors]})


# [url]/actors/full=[full_name]
@app.route('/actors/full=<full_name>', methods = ['GET'])
def get_actors_by_full_name(full_name):
    query_name = "%{}%".format(full_name)
    actors = Actor.query.filter(Actor.full_name.like(query_name)).all()
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


# Query Movies by Year
# [url]/movies/year=[year]
@app.route('/movies/year=<year>', methods=['GET'])
def get_movies_by_year(year):
    try:
        movies = Movie.query.filter_by(year=year)
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


# Query TV Shows by Years Running
# [url]/tv_shows/year=[year]
@app.route('/tv_shows/year=<year>', methods=['GET'])
def get_tv_shows_by_year(year):
    try:
        queried_year = year
        tv_shows = list()

        # Get list of all TVShows
        all_tv_shows = TVShows.query.all()

        for tv_show in all_tv_shows:
            tv_show_year = tv_show.year
            years_running = list()

            # Ongoing Show
            if tv_show_year[-1] == '-':
                y = int(tv_show_year[:-1])
                current_year = datetime.datetime.now().year
                while y <= current_year:
                    years_running.append(str(y))
                    y += 1

            # Show Ran for Multiple Years
            elif tv_show_year[4] == '-':
                y = int(tv_show_year[:4])
                end_year = int(tv_show_year[5:])
                while y <= end_year:
                    years_running.append(str(y))
                    y += 1

            # Show Ran for One Year
            else:
                if int(tv_show_year) == queried_year:
                    years_running.append(tv_show_year)

            # Add TV Show to List if it was running during the queried year
            for temp in years_running:
                if temp == queried_year:
                    tv_shows.append(tv_show)
                    break

        return jsonify({'tv_shows': [tv_show.serialize() for tv_show in tv_shows]})
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run(port=port)
