from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import date, timedelta
import pymysql
import os
import math

# Setup App
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])  # Should change based on is in Development or Production
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS
CORS(app)

# Start Database
db = SQLAlchemy(app)

# Enable Variable Port for Heroku
port = int(os.environ.get('PORT', 33507))

# Import models
from models import Actor, ActorMovie, ActorsTVShow
from media_models import Genre
from media_models import Movie, MovieGenre
from media_models import TVShows, TVShowGenre, TVShowSeasons, TVShowEpisodes, TVShowInfo

# Force pymysql to be used as replacement for MySQLdb
pymysql.install_as_MySQLdb()


# [url]/
@app.route('/')
def hello_world():
    return 'Hello World!'


# [url]/recently_added
@app.route('/recently_added/page=<int:page>', methods=['GET'])
@app.route('/recently_added', methods=['GET'])
def recently_added(page=1):
    try:
        results = list()
        today = date.today()

        # Append all movies in database within 'RECENT_TIME' days
        movies = Movie.query.order_by().all()
        for movie in movies:
            date_movie_added = movie.date_added

            if date_movie_added + timedelta(app.config['RECENT_TIME']) >= today:
                results.append(movie)

        # Append all tv-shows in database within 'RECENT_TIME' days
        tv_shows = TVShows.query.order_by().all()
        for tv_show in tv_shows:
            date_tv_show_added = tv_show.date_added

            if date_tv_show_added + timedelta(app.config['RECENT_TIME']) >= today:
                results.append(tv_show)

        return paginated_json('recently_added', results, page)
    except Exception as e:
        return str(e)


# Search All Route
# [url]/all=[query]
@app.route('/all=<query>/page=<int:page>', methods=['GET'])
@app.route('/all=<query>', methods=['GET'])
@app.route('/all=', methods=['GET'])
def get_all_results(query=None, page=1):
    try:
        results = list()

        # Append all movies in database with matching query
        movies = get_movies_search_all(query, True)
        for movie in movies:
            results.append(movie)

        # Append all tv-shows in database with matching query
        tv_shows = get_tv_shows_search_all(query, True)
        for tv_show in tv_shows:
            results.append(tv_show)

        return paginated_json('all', results, page)
    except Exception as e:
        return str(e)


# Individual Media Info Route
@app.route('/title=<title>/info', methods=['GET'])
def get_media_info(title=None):
    try:
        # Check if title is in TV Show Table
        check = TVShows.query.filter_by(title=title).first()

        if check is not None:
            result = get_tv_show_info(title)
            if result is not None:
                return jsonify({title: [tv_info.serialize() for tv_info in result]})

        # Check if title is in Movie Table
        check = Movie.query.filter_by(title=title).first()
        if check is not None:
            # Check if title is in Movie Table
            result = get_movie_info(title)
            if result is not None:
                return jsonify({title: result.serialize()})

        return list()
    except Exception as e:
        return str(e)


# [url]/actors
# [url]/actors/page=[page_number]
@app.route('/actors/page=<int:page>', methods=['GET'])
@app.route('/actors/page=', methods=['GET'])
@app.route('/actors', methods=['GET'])
def get_actors_by_page(page=1):
    try:
        actors = Actor.query.order_by().all()
        max_page = int(math.ceil(actors[-1].id / app.config['POSTS_PER_PAGE']))
        actors = list()

        # Create a tuple of actors in alphabetical order
        pagination = Actor.query.order_by(Actor.full_name).paginate(page, app.config['POSTS_PER_PAGE'], error_out=False)

        # Create a list of Actor objects of size app.config['POST_PER_PAGE']
        for item in pagination.items:
            actors.append(Actor.query.filter_by(id=item.id).first())

        json = make_response(jsonify({'actors': [actor.serialize() for actor in actors]}))
        json.headers['current_page'] = page
        json.headers['max_pages'] = max_page
        return json
    except Exception as e:
        return str(e)


# [url]/actors/fn=[first_name]/page=[page_number]
# [url]/actors/fn=[first_name]
@app.route('/actors/fn=<first_name>/page=<int:page>', methods=['GET'])
@app.route('/actors/fn=<first_name>', methods=['GET'])
@app.route('/actors/fn=', methods=['GET'])
def get_actors_by_first_name(first_name=None, search_all=False,page=1):
    try:
        query_name = "{}%".format(first_name)
        actors_first_name = Actor.query.filter(Actor.first_name.like(query_name)).all()

        return paginated_json('actors', actors_first_name, page)
    except Exception as e:
        return str(e)


# [url]/actors/ln=[last_name]/page=[page_number]
# [url]/actors/ln=[last_name]
@app.route('/actors/ln=<last_name>/page=<int:page>')
@app.route('/actors/ln=<last_name>', methods=['GET'])
@app.route('/actors/ln=', methods=['GET'])
def get_actors_by_last_name(last_name=None, page=1):
    try:
        query_name = "{}%".format(last_name)
        actors_last_name = Actor.query.filter(Actor.last_name.like(query_name)).all()
        return paginated_json('actors', actors_last_name, page)
    except Exception as e:
        return str(e)


# also serves as the actors search all function
# [url]/actors/all=[query]/page=[page_number]
# [url]/actors/all=[query]
# [url]/actors/full=[full_name]/page=[page_number]
# [url]/actors/full=[full_name]
@app.route('/actors/all=<full_name>/page=<int:page>', methods=['GET'])
@app.route('/actors/all=<full_name>', methods=['GET'])
@app.route('/actors/all=', methods=['GET'])
@app.route('/actors/full=<full_name>/page=<int:page>', methods=['GET'])
@app.route('/actors/full=<full_name>', methods=['GET'])
@app.route('/actors/full=', methods=['GET'])
def get_actors_by_full_name(full_name=None, search_all=False, page=1):
    try:
        query_name = "%{}%".format(full_name)
        actors_full_name = Actor.query.filter(Actor.full_name.like(query_name)).all()
        return paginated_json('actors', actors_full_name, page)
    except Exception as e:
        return str(e)


# Query All Movies in Database
# [url]/movies
@app.route('/movies', methods=['GET'])
def get_movies():
    try:
        movies = Movie.query.all()
        return jsonify({'movies': [movie.serialize() for movie in movies]})
    except Exception as e:
        return str(e)


# post to movies database CHANGE THE ROUTE IF NECESSARY
@app.route('/movies', methods=['POST'])
def post_movie():
    data = request.get_json()
    title = str(data['title'])
    year = str(data['year'])
    service = str(data['service'])
    tag = str(data['tag'])
    url = str(data['url'])
    date_added = str(date.today())
    image_url = str(data['image_url'])

    try:
        movie = Movie(
            title=title,
            year=year,
            service=service,
            tag=tag,
            url=url,
            date_added=date_added,
            image_url=image_url
        )
        db.session.add(movie)
        db.session.commit()
        return "Movie Added"
    except Exception as e:
        return str(e)


# [url]/movies/title=[title]/info
@app.route('/movies/title=<title>/info', methods=['GET'])
def get_movie_info(title=None):
    try:
        if title is not None:
            movie = Movie.query.filter_by(title=title).first()

            if movie is not None:
                return jsonify({title: movie.serialize()})
        return None
    except Exception as e:
        return str(e)


# [url/movies/recently_added
@app.route('/movies/recently_added/page=<int:page>', methods=['GET'])
@app.route('/movies/recently_added', methods=['GET'])
def get_movies_recent(page=1):
    try:
        results = list()
        today = date.today()

        # Append all movies in database within 'RECENT_TIME' days
        movies = Movie.query.order_by().all()
        for movie in movies:
            date_movie_added = movie.date_added

            if date_movie_added + timedelta(app.config['RECENT_TIME']) >= today:
                results.append(movie)

        return paginated_json('movies', results, page)
    except Exception as e:
        return str(e)


# [url]/movies/title=[title]
@app.route('/movies/title=<title>/page=<int:page>', methods=['GET'])
@app.route('/movies/title=<title>', methods=['GET'])
@app.route('/movies/title=', methods=['GET'])
def get_movies_by_title(title=None, search_all=False, page=1):
    try:
        query_title = "%{}%".format(title)
        movies = Movie.query.filter(Movie.title.like(query_title)).all()

        # return list for search all route
        if search_all:
            movie_list = list()
            for movie in movies:
                movie_list.append(movie)
            return movies

        # return json of queried movies
        else:
            return paginated_json('movies', movies, page)
    except Exception as e:
        return str(e)


# Query Movies by Service Provider
# [url]/movies/service=[service_provider]
@app.route('/movies/service=<service>/page=<int:page>', methods=['GET'])
@app.route('/movies/service=<service>', methods=['GET'])
@app.route('/movies/service=', methods=['GET'])
def get_movies_by_service(service=None, search_all=False, page=1):
    try:
        results = list()
        movies = Movie.query.filter_by(service=service)

        # return list for search all route
        if search_all:
            movie_list = list()
            for movie in movies:
                movie_list.append(movie)
            return movie_list

        for movie in movies:
            results.append(movie)

        # return json of queried movies
        else:
            return paginated_json('movies', results, page)
    except Exception as e:
        return str(e)


# Query Movies by Genre Type
# [url]/movies/genre=[genre_type]
@app.route('/movies/genre=<genre>/page=<int:page>', methods=['GET'])
@app.route('/movies/genre=<genre>', methods=['GET'])
@app.route('/movies/genre=', methods=['GET'])
def get_movies_by_genre(genre=None, search_all=False, page=1):
    try:
        movies = list()

        # Determine Singular Genre Object
        genre = Genre.query.filter_by(genre_type=genre).first()

        # if Genre exists, query Movies
        if genre is not None:
            # Determine all Movie_ids with that Genre
            movie_genre_rel = MovieGenre.query.filter_by(genre_id=genre.id)

            # Create a list of all Movie_ids with that Genre
            movie_ids = list()
            for mgr in movie_genre_rel:
                movie_ids.append(mgr.movie_id)

            # Create a list of all the corresponding Movie objects
            for id in movie_ids:
                movies.append(Movie.query.filter_by(id=id).first())

        # return list for search all route
        if search_all:
            movie_list = list()
            for movie in movies:
                movie_list.append(movie)
            return movie_list

        else:
            return paginated_json('movies', movies, page)
    except Exception as e:
        return str(e)


# Query Movies by Year
# [url]/movies/year=[year]
@app.route('/movies/year=<year>/page=<int:page>', methods=['GET'])
@app.route('/movies/year=<year>', methods=['GET'])
@app.route('/movies/year=', methods=['GET'])
def get_movies_by_year(year=None, search_all=False, page=1):
    try:
        movies = list()
        if year is not None and int(year) > 0:
            movies = Movie.query.filter_by(year=year)

            movie_list = list()
            for movie in movies:
                movie_list.append(movie)

            # return list for search all route
            if search_all:
                return movie_list
            else:
                return paginated_json('movies', movie_list, page)

        # return json of queried movies
        else:
            return paginated_json('movies', movies, page)
    except Exception as e:
        return str(e)


# [url]/movies/actor=[actor_full_name]/page=[page]
# [url]/movies/actor=[actor_full_name]
@app.route('/movies/actor=<actor_name>/page=<int:page>', methods=['GET'])
@app.route('/movies/actor=<actor_name>', methods=['GET'])
@app.route('/movies/actor=', methods=['GET'])
def get_movies_by_actor(actor_name=None, page=1):
    try:
        movies = list()
        actor_name = Actor.query.filter_by(full_name=actor_name).first()
        if actor_name is not None:
            movie_actor_rel = ActorMovie.query.filter_by(actor_id=actor_name.id)
            movie_id = list()
            for mar in movie_actor_rel:
                movie_id.append(mar.movie_id)
            for id in movie_id:
                movies.append(Movie.query.filter_by(id=id).first())

        return paginated_json("movies", movies, page)
    except Exception as e:
        return str(e)


# Return a list of movies that match query in any column
@app.route('/movies/all=<query>/page=<int:page>', methods=['GET'])
@app.route('/movies/all=<query>', methods=['GET'])
@app.route('/movies/all=', methods=['GET'])
def get_movies_search_all(query=None, search_all=False, page=1):
    try:
        movies = list()

        # movie_title = query
        movies_title = get_movies_by_title(query, True)
        if len(movies_title) != 0:
            for movie in movies_title:
                movies.append(movie)

        # movie_service = query
        movies_service = get_movies_by_service(query, True)
        if len(movies_service) != 0:
            for movie in movies_service:
                movies.append(movie)

        # movie_genre = query
        movies_genre = get_movies_by_genre(query, True)
        if len(movies_genre) != 0:
            for movie in movies_genre:
                movies.append(movie)

        # movie_year = query
        movies_year = get_movies_by_year(query, True)
        if len(movies_year) != 0:
            for movie in movies_year:
                movies.append(movie)

        i = 0
        while i < len(movies):
            if isinstance(movies[i], str):
                movies.remove(movies[i])
                i -= 1
            i += 1

        # Ensure no duplicates and sorted
        movies = list(set(movies))
        movies = sorted(movies, key=lambda movie: movie.id)

        if search_all:
            return movies
        else:
            return paginated_json('movies', movies, page)
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


# post to tv_shows database CHANGE THE ROUTE IF NECESSARY
@app.route('/tv_shows', methods=['POST'])
def post_tv_shows():
    data = request.get_json()
    title = str(data['title'])
    year = str(data['year'])
    service = str(data['service'])
    tag = str(data['tag'])
    url = str(data['url'])
    num_episodes = int(data['num_episodes'])
    num_seasons = int(data['num_seasons'])
    date_added = str(date.today())
    image_url = str(data['image_url'])

    try:
        tv_show = TVShows(
            title=title,
            year=year,
            service=service,
            tag=tag,
            url=url,
            num_episodes=num_episodes,
            num_seasons=num_seasons,
            date_added=date_added,
            image_url=image_url
        )
        db.session.add(tv_show)
        db.session.commit()
        return "TV Show Added"
    except Exception as e:
        return str(e)


# [url]/tv_shows/title=[title]/info
@app.route('/tv_shows/title=<title>/info', methods=['GET'])
def get_tv_show_info(title=None):
    try:
        tv_info = list()

        tv_show = TVShows.query.filter_by(title=title).first()
        tv_show_id = tv_show.id
        if tv_show_id is not None:
            # Get List of all entries
            tv_show_seasons = TVShowSeasons.query.filter_by(tv_show_id=tv_show_id)

            # For each season
            for tss in tv_show_seasons:

                # Get all episodes in the season
                season_id = tss.season
                season_episodes = TVShowEpisodes.query.filter_by(tv_show_id=tv_show_id).filter_by(season_id=season_id)

                episodes = list()
                # For each episode
                for ep in season_episodes:
                    episodes.append(ep)

                entry = TVShowInfo(season_id, episodes)
                tv_info.append(entry)

        # Display Every Season
        return jsonify({title: [tvi.serialize() for tvi in tv_info]})
    except Exception as e:
        return str(e)


# [url/tv_shows/recently_added
@app.route('/tv_shows/recently_added/page=<int:page>', methods=['GET'])
@app.route('/tv_shows/recently_added', methods=['GET'])
def get_tv_shows_recent(page=1):
    try:
        results = list()
        today = date.today()

        # Append all movies in database within 'RECENT_TIME' days
        tv_shows = TVShows.query.order_by().all()
        for tv_show in tv_shows:
            date_tv_show_added = tv_show.date_added

            if date_tv_show_added + timedelta(app.config['RECENT_TIME']) >= today:
                results.append(tv_show)

        return paginated_json('tv_shows', results, page)
    except Exception as e:
        return str(e)


# [url]/tv_shows/title=[title]/page=[page]
# [url]/tv_shows/title=[title]
@app.route('/tv_shows/title=<title>/page=<int:page>', methods=['GET'])
@app.route('/tv_shows/title=<title>', methods=['GET'])
@app.route('/tv_shows/title=', methods=['GET'])
def get_tv_shows_by_title(title=None, search_all=False, page=1):
    try:
        query_title = "%{}%".format(title)
        tv_shows = TVShows.query.filter(TVShows.title.like(query_title)).all()

        # return list for search all route
        if search_all:
            tv_list = list()
            for tv_show in tv_shows:
                tv_list.append(tv_show)
            return tv_list

        # return json of queried tv_shows
        else:
            return paginated_json('tv_shows', tv_shows, page)
    except Exception as e:
        return str(e)


# Query TV Shows by Service Provider
# [url]/tv_shows/service=[service_provider]
@app.route('/tv_shows/service=<service>/page=<int:page>', methods=['GET'])
@app.route('/tv_shows/service=<service>', methods=['GET'])
@app.route('/tv_shows/service=', methods=['GET'])
def get_tv_shows_by_service(service=None, search_all=False, page=1):
    try:
        results = list()
        tv_shows = TVShows.query.filter_by(service=service)

        # return list for search all route
        if search_all:
            tv_list = list()
            for tv_show in tv_shows:
                tv_list.append(tv_show)
            return tv_list

        for tv_show in tv_shows:
            results.append(tv_show)

        else:
            return paginated_json('tv_shows', results, page)
    except Exception as e:
        return str(e)


# Query TV Shows by Genre Type
# [url]/tv_shows/genre=[genre_type]
@app.route('/tv_shows/genre=<genre>/page=<int:page>', methods=['GET'])
@app.route('/tv_shows/genre=<genre>', methods=['GET'])
@app.route('/tv_shows/genre=', methods=['GET'])
def get_tv_shows_by_genre(genre=None, search_all=False, page=1):
    try:
        tv_shows = list()

        # Determine Singular Genre Object
        genre = Genre.query.filter_by(genre_type=genre).first()

        # If Genre exists, query TV_Shows
        if genre is not None:
            # Determine all tvshow_ids with that Genre ID
            tvshow_genre_rel = TVShowGenre.query.filter_by(genre_id=genre.id)

            # Create a list of all TV_Show ids with that Genre
            tvshow_ids = list()
            for tgr in tvshow_genre_rel:
                tvshow_ids.append(tgr.tv_show_id)

            # Create a list of all the corresponding TV_Show objects
            for id in tvshow_ids:
                tv_shows.append(TVShows.query.filter_by(id=id).first())

        # return list for search all route
        if search_all:
            tv_list = list()
            for tv_show in tv_shows:
                tv_list.append(tv_show)
            return tv_list

        # return json of queried tv_shows
        else:
            return paginated_json('tv_shows', tv_shows, page)
    except Exception as e:
        return str(e)


# Query TV Shows by Years Running
# [url]/tv_shows/year=[year]
@app.route('/tv_shows/year=<year>/page=<int:page>', methods=['GET'])
@app.route('/tv_shows/year=<year>', methods=['GET'])
@app.route('/tv_shows/year=', methods=['GET'])
def get_tv_shows_by_year(year=None, search_all=False, page=1):
    try:
        tv_shows = list()

        if year is not None and int(year) > 0:
            queried_year = year

            # Get list of all TVShows
            all_tv_shows = TVShows.query.all()

            for tv_show in all_tv_shows:
                tv_show_year = tv_show.year
                years_running = list()

                # Ongoing Show
                if tv_show_year[-1] == '-':
                    y = int(tv_show_year[:-1])
                    current_year = date.today().year
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

        # return list for search all route
        if search_all:
            tv_list = list()
            for tv_show in tv_shows:
                tv_list.append(tv_show)
            return tv_list

        # return json of queried tv_shows
        else:
            return paginated_json('tv_shows', tv_shows, page)
    except Exception as e:
        return str(e)


# [url]/tv_shows/actor=[actor_full_name]/page=[page]
# [url]/tv_shows/actor=[actor_full_name]
@app.route('/tv_shows/actor=<actor_name>/page=<int:page>', methods=['GET'])
@app.route('/tv_shows/actor=<actor_name>', methods=['GET'])
@app.route('/tv_shows/actor=', methods=['GET'])
def get_tv_shows_by_actor(actor_name=None, search_all=False, page=1):
    try:
        tv_shows = list()
        actor_name = Actor.query.filter_by(full_name=actor_name).first()
        if actor_name is not None:
            tv_shows_actor_rel = ActorsTVShow.query.filter_by(actors_id=actor_name.id)
            tv_shows_id = list()
            for tar in tv_shows_actor_rel:
                tv_shows_id.append(tar.tv_show_id)
            for id in tv_shows_id:
                tv_shows.append(TVShows.query.filter_by(id=id).first())
        if search_all:
            return tv_shows

        else:
            return paginated_json('tv_shows', tv_shows, page)
    except Exception as e:
        return str(e)


# Return a list of tv_shows that match query in any column
@app.route('/tv_shows/all=<query>/page=<int:page>', methods=['GET'])
@app.route('/tv_shows/all=<query>', methods=['GET'])
@app.route('/tv_shows/all=', methods=['GET'])
def get_tv_shows_search_all(query=None, search_all=False, page=1):
    try:
        tv_shows = list()

        # tv-show_title = query
        tv_shows_title = get_tv_shows_by_title(query, True)
        if len(tv_shows_title) != 0:
            for tv_show in tv_shows_title:
                tv_shows.append(tv_show)

        # tv-show_service = query
        tv_shows_service = get_tv_shows_by_service(query, True)
        if len(tv_shows_service) != 0:
            for tv_show in tv_shows_service:
                tv_shows.append(tv_show)

        # tv-show genre = query
        tv_shows_genre = get_tv_shows_by_genre(query, True)
        if len(tv_shows_genre) != 0:
            for tv_show in tv_shows_genre:
                tv_shows.append(tv_show)

        # tv-show year = query
        tv_shows_year = get_tv_shows_by_year(query, True)
        if len(tv_shows_year) != 0:
            for tv_show in tv_shows_year:
                tv_shows.append(tv_show)

        # tv-show actor_full_name = query
        tv_shows_actors = get_tv_shows_by_actor(query, True)
        if len(tv_shows_actors) != 0:
            for tv_show in tv_shows_actors:
                tv_shows.append(tv_show)

        i = 0
        while i < len(tv_shows):
            if isinstance(tv_shows[i], str):
                tv_shows.remove(tv_shows[i])
                i -= 1
            i += 1

        # Ensure no duplicates and sorted
        tv_shows = list(set(tv_shows))
        tv_shows = sorted(tv_shows, key=lambda tv_show: tv_show.id)

        if search_all:
            return tv_shows
        else:
            return paginated_json('tv_shows', tv_shows, page)
    except Exception as e:
        return str(e)


# Individual Movie Info
def get_movie_info(title):
    try:
        movie = Movie.query.filter_by(title=title).first()

        if movie is not None:
            return movie

        return None
    except Exception as e:
        return str(e)


# Individual TV Show Info
def get_tv_show_info(title):
    try:
        tv_info = list()

        tv_show = TVShows.query.filter_by(title=title).first()
        tv_show_id = tv_show.id
        if tv_show_id is not None:
            # Get List of all entries
            tv_show_seasons = TVShowSeasons.query.filter_by(tv_show_id=tv_show_id)

            # For each season
            for tss in tv_show_seasons:

                # Get all episodes in the season
                season_id = tss.season
                season_episodes = TVShowEpisodes.query.filter_by(tv_show_id=tv_show_id).filter_by(season_id=season_id)

                episodes = list()
                # For each episode
                for ep in season_episodes:
                    episodes.append(ep)

                entry = TVShowInfo(season_id, episodes)
                tv_info.append(entry)

            # Display Every Season
            return tv_info
        else:
            return None
    except Exception as e:
        return str(e)


# Pseudo Pagination
def pseudo_paginate(page: int, list_to_paginate: []):
    start_page = (page - 1) * app.config['POSTS_PER_PAGE']
    end_page = start_page + app.config['POSTS_PER_PAGE']
    if end_page > len(list_to_paginate):
        end_page = len(list_to_paginate)

    return list_to_paginate[start_page:end_page]


# Return json
def paginated_json(json_name: str, queried_results: [], page: int):
    num_pages = max_pages(queried_results)

    # Paginate results
    results = pseudo_paginate(page, queried_results)

    json = make_response(jsonify({json_name: [result.serialize() for result in results]}))
    json.headers['current_page'] = page
    json.headers['max_pages'] = num_pages

    # Headers the Client is Allowed to Access
    json.headers['Access-Control-Expose-Headers'] = 'current_page, max_pages'
    return json


# Return max pages for specified query
def max_pages(queried_list: []):
    return int(math.ceil(len(queried_list) / app.config['POSTS_PER_PAGE']))


if __name__ == '__main__':
    app.run(port=port)
