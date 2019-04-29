import math
import os
from datetime import date, timedelta

import pymysql
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Setup App
app = Flask(__name__)
app.config.from_object('config.TestingConfig')  # Should change based on is in Development or Production
# app.config.from_object(os.environ['APP_SETTINGS'])  # Should change based on is in Development or Production
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS
CORS(app)

# Start Database
db = SQLAlchemy(app)

# Enable Variable Port for Heroku
port = int(os.environ.get('PORT', 33507))

# Import models
from models.models import Actor, ActorMovie, ActorsTVShow
from models.media_models import Genre
from models.media_models import Movie, MovieGenre, MovieInfo
from models.media_models import TVShows, TVShowGenre, TVShowSeasons, TVShowEpisodes, TVShowSeasonInfo, TVShowInfo

# Force pymysql to be used as replacement for MySQLdb
pymysql.install_as_MySQLdb()


# [url]/
@app.route('/')
def hello_world():
    return 'Home Page'


# [url]/recently_added
@app.route('/recently_added/page=<page>', methods=['GET'])
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


# Individual Media Info Route
@app.route('/title=<title>/info', methods=['GET'])
@app.route('/title=/info', methods=['GET'])
def get_media_info(title=None):
    # Check if title is in TV Show Table
    check = TVShows.query.filter_by(title=title).first()

    if check is not None:
        result = tv_show_info(title)
        if result is not None:
            return jsonify({title: result.serialize()})

    # Check if title is in Movie Table
    check = Movie.query.filter_by(title=title).first()
    if check is not None:
        # Check if title is in Movie Table
        result = movie_info(title)
        if result is not None:
            return jsonify({title: result.serialize()})

    return jsonify({'title': []})


# [url]/actors
# [url]/actors/page=[page_number]
@app.route('/actors/page=<page>', methods=['GET'])
@app.route('/actors/page=', methods=['GET'])
@app.route('/actors', methods=['GET'])
def get_actors_by_page(page=1):
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


# [url]/actors/fn=[first_name]/page=[page_number]
# [url]/actors/fn=[first_name]
@app.route('/actors/fn=<first_name>/page=<page>', methods=['GET'])
@app.route('/actors/fn=<first_name>', methods=['GET'])
@app.route('/actors/fn=', methods=['GET'])
def get_actors_by_first_name(first_name=None, search_all=False, page=1):
    query_name = "{}%".format(first_name)
    actors_first_name = Actor.query.filter(Actor.first_name.like(query_name)).all()
    if search_all:
        actors_list = list()
        for actor in actors_first_name:
            actors_list.append(actor)
        return actors_list

    return paginated_json('actors', actors_first_name, page)


# [url]/actors/ln=[last_name]/page=[page_number]
# [url]/actors/ln=[last_name]
@app.route('/actors/ln=<last_name>/page=<page>', methods=['GET'])
@app.route('/actors/ln=<last_name>', methods=['GET'])
@app.route('/actors/ln=', methods=['GET'])
def get_actors_by_last_name(last_name=None, search_all=False, page=1):
    query_name = "{}%".format(last_name)
    actors_last_name = Actor.query.filter(Actor.last_name.like(query_name)).all()
    if search_all:
        actors_list = list()
        for actor in actors_last_name:
            actors_list.append(actor)
        return actors_list

    return paginated_json('actors', actors_last_name, page)


# also serves as the actors search all function
# [url]/actors/full=[full_name]/page=[page_number]
# [url]/actors/full=[full_name]
@app.route('/actors/full=<full_name>/page=<page>', methods=['GET'])
@app.route('/actors/full=<full_name>', methods=['GET'])
@app.route('/actors/full=', methods=['GET'])
def get_actors_by_full_name(full_name=None, search_all=False, page=1):
    query_name = "%{}%".format(full_name)
    actors_full_name = Actor.query.filter(Actor.full_name.like(query_name)).all()
    if search_all:
        actors_full_name_list = list()
        for actor in actors_full_name:
            actors_full_name_list.append(actor)
        return actors_full_name_list
    return paginated_json('actors', actors_full_name, page)


# Return a list of tv_shows that match query in any column
# [url]/actors/all=[query]/page=[page_number]
# [url]/actors/all=[query]
@app.route('/actors/all=<query>/page=<page>', methods=['GET'])
@app.route('/actors/all=<query>', methods=['GET'])
@app.route('/actors/all=', methods=['GET'])
def get_actor_search_all(query=None, search_all=False, page=1):
    actors = list()
    if query is not None:
        actors_by_first_name = get_actors_by_first_name(query, True)
        if len(actors_by_first_name) != 0:
            for actor in actors_by_first_name:
                actors.append(actor)

        actors_by_last_name = get_actors_by_last_name(query, True)
        if len(actors_by_last_name) != 0:
            for actor in actors_by_last_name:
                actors.append(actor)

        actors_by_full_name = get_actors_by_full_name(query, True)
        if len(actors_by_full_name) != 0:
            for actor in actors_by_full_name:
                actors.append(actor)

        i = 0
        while i < len(actors):
            if isinstance(actors[i], str):
                actors.remove(actors[i])
                i -= 1
            i += 1

        # Ensure no duplicates and sorted
        actors = list(set(actors))
        actors = sorted(actors, key=lambda actor: actor.id)

    if search_all:
        return actors
    else:
        return paginated_json('actors', actors, page)


# Query All Movies in Database
# [url]/movies
@app.route('/movies', methods=['GET'])
def get_movies():
    movies = Movie.query.all()
    return jsonify({'movies': [movie.serialize() for movie in movies]})


# post to movies database CHANGE THE ROUTE IF NECESSARY
@app.route('/post_movie', methods=['POST'])
def post_movie():
    data = request.get_json()
    title = str(data['title'])
    year = str(data['year'])
    service = str(data['service'])
    tag = str(data['tag'])
    url = str(data['url'])
    date_added = str(date.today())
    image_url = str(data['image_url'])
    genre_type = str(data['genre_type'])
    description = str(data['description'])

    success_check = True
    title_check = True
    year_check = True
    service_check = True
    tag_check = True
    url_check = True
    image_url_check = True
    genre_type_check = True
    description_check = True

    # parse genre_type
    genre_str_list = [genre.strip() for genre in genre_type.split(',')]
    genre_ids = list()

    for genre in genre_str_list:
        if Genre.query.filter_by(genre_type=genre).scalar() is None:
            success_check = False
            genre_type_check = False

    if title is "" or Movie.query.filter_by(title=title).scalar() is not None:
        success_check = False
        title_check = False
    if len(year) is not 4 or year.isdigit() is False:
        success_check = False
        year_check = False
    if service is "":
        success_check = False
        service_check = False
    if tag is "":
        success_check = False
        tag_check = False
    if url is "" or Movie.query.filter_by(url=url).scalar() is not None:
        success_check = False
        url_check = False
    if image_url is "" or Movie.query.filter_by(image_url=image_url).scalar() is not None:
        success_check = False
        image_url_check = False
    if genre_type is "":
        success_check = False
        genre_type_check = False
    if description is "":
        success_check = False
        description_check = False
    if success_check is False:
        return jsonify({'success': success_check,
                        'valid_title': title_check,
                        'valid_year': year_check,
                        'valid_service': service_check,
                        'valid_tag': tag_check,
                        'valid_url': url_check,
                        'valid image_url': image_url_check,
                        'valid_genre_type': genre_type_check,
                        'valid_description': description_check, })

    # get list of all genres_ids
    for genre in genre_str_list:
        genre_ids.append(Genre.query.filter_by(genre_type=genre).first().id)

    try:
        movie = Movie(
            title=title,
            year=year,
            service=service,
            tag=tag,
            url=url,
            date_added=date_added,
            image_url=image_url,
            description=description
        )
        db.session.add(movie)
        movie_id = Movie.query.filter_by(title=title).first().id

        for genre_id in genre_ids:
            movie_genre = MovieGenre(
                movie_id=movie_id,
                genre_id=genre_id
            )
            db.session.add(movie_genre)
        db.session.commit()
        return jsonify({'success': success_check,
                        'valid_title': title_check,
                        'valid_year': year_check,
                        'valid_service': service_check,
                        'valid_tag': tag_check,
                        'valid_url': url_check,
                        'valid image_url': image_url_check,
                        'valid_genre_type': genre_type_check,
                        'valid_description': description_check, })
    except Exception as e:
        return str(e)


# [url]/movies/title=[title]/info
@app.route('/movies/title=<title>/info', methods=['GET'])
@app.route('/movies/title=/info', methods=['GET'])
def get_movie_info(title=None):
    if title is not None:
        movie = Movie.query.filter_by(title=title).first()

        if movie is not None:
            return jsonify({title: movie.serialize()})
    return jsonify({'title': None})


# [url/movies/recently_added
@app.route('/movies/recently_added/page=<page>', methods=['GET'])
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
@app.route('/movies/title=<title>/page=<page>', methods=['GET'])
@app.route('/movies/title=<title>', methods=['GET'])
@app.route('/movies/title=', methods=['GET'])
def get_movies_by_title(title=None, search_all=False, page=1):
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


# Query Movies by Service Provider
# [url]/movies/service=[service_provider]
@app.route('/movies/service=<service>/page=<page>', methods=['GET'])
@app.route('/movies/service=<service>', methods=['GET'])
@app.route('/movies/service=', methods=['GET'])
def get_movies_by_service(service=None, search_all=False, page=1):
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


# Query Movies by Genre Type
# [url]/movies/genre=[genre_type]
@app.route('/movies/genre=<genre>/page=<page>', methods=['GET'])
@app.route('/movies/genre=<genre>', methods=['GET'])
@app.route('/movies/genre=', methods=['GET'])
def get_movies_by_genre(genre=None, search_all=False, page=1):
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


# Query Movies by Year
# [url]/movies/year=[year]
@app.route('/movies/year=<year>/page=<page>', methods=['GET'])
@app.route('/movies/year=<year>', methods=['GET'])
@app.route('/movies/year=', methods=['GET'])
def get_movies_by_year(year=None, search_all=False, page=1):
    movies = list()
    if year is not None and year.isdigit():
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
        if search_all:
            return movies
        else:
            return paginated_json('movies', movies, page)


# [url]/movies/actor=[actor_full_name]/page=[page]
# [url]/movies/actor=[actor_full_name]
@app.route('/movies/actor=<actor_name>/page=<page>', methods=['GET'])
@app.route('/movies/actor=<actor_name>', methods=['GET'])
@app.route('/movies/actor=', methods=['GET'])
def get_movies_by_actor(actor_name=None, page=1):
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


# Return a list of movies that match query in any column
@app.route('/movies/all=<query>/page=<page>', methods=['GET'])
@app.route('/movies/all=<query>', methods=['GET'])
@app.route('/movies/all=', methods=['GET'])
def get_movies_search_all(query=None, search_all=False, page=1):
    movies = list()

    if query is not None:

        # movie_title = query
        movies_title = get_movies_by_title(query, True)
        if len(movies_title) > 0:
            for movie in movies_title:
                movies.append(movie)

        # movie_service = query
        movies_service = get_movies_by_service(query, True)
        if len(movies_service) > 0:
            for movie in movies_service:
                movies.append(movie)

        # movie_genre = query
        movies_genre = get_movies_by_genre(query, True)
        if len(movies_genre) > 0:
            for movie in movies_genre:
                movies.append(movie)

        # movie_year = query
        movies_year = get_movies_by_year(query, True)
        if len(movies_year) > 0:
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

    return paginated_json('movies', movies, page)


# Query All TV Shows in Database
# [url]/tv_shows
@app.route('/tv_shows', methods=['GET'])
def get_tv_shows():
    tv_shows = TVShows.query.all()
    return jsonify({'tv_shows': [tv_show.serialize() for tv_show in tv_shows]})


# post to tv_shows database CHANGE THE ROUTE IF NECESSARY
@app.route('/post_tv_show', methods=['POST'])
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
    genre_type = str(data['genre_type'])
    description = str(data['description'])

    success_check = True
    title_check = True
    year_check = True
    service_check = True
    tag_check = True
    url_check = True
    num_episodes_check = True
    num_seasons_check = True
    image_url_check = True
    genre_type_check = True
    description_check = True

    # parse genre_type
    genre_str_list = [genre.strip() for genre in genre_type.split(',')]
    genre_ids = list()

    for genre in genre_str_list:
        if Genre.query.filter_by(genre_type=genre).scalar() is None:
            success_check = False
            genre_type_check = False

    if title is "" or TVShows.query.filter_by(title=title).scalar() is not None:
        success_check = False
        title_check = False
    if len(year) is not 4 or not isinstance(year, int):
        success_check = False
        year_check = False
    if service is "":
        success_check = False
        service_check = False
    if tag is "":
        success_check = False
        tag_check = False
    if url is "" or TVShows.query.filter_by(url=url).scalar() is not None:
        success_check = False
        url_check = False
    if num_episodes > 0:
        success_check = False
        num_episodes_check = False
    if num_seasons > 0:
        success_check = False
        num_seasons_check = False
    if image_url is "" or TVShows.query.filter_by(image_url=image_url).scalar() is not None:
        success_check = False
        image_url_check = False
    if genre_type is "":
        success_check = False
        genre_type_check = False
    if description is "":
        success_check = False
        description_check = False
    if success_check is "":
        return jsonify({'success': success_check,
                        'valid_title': title_check,
                        'valid_year': year_check,
                        'valid_service': service_check,
                        'valid_tag': tag_check,
                        'valid_url': url_check,
                        'valid_num_episodes': num_episodes_check,
                        'valid_num_seasons': num_seasons_check,
                        'valid image_url': image_url_check,
                        'valid_genre_type': genre_type_check,
                        'valid_description': description_check, })

    # get list of all genres_ids
    for genre in genre_str_list:
        genre_ids.append(Genre.query.filter_by(genre_type=genre).first().id)

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
            image_url=image_url,
            description=description
        )
        db.session.add(tv_show)

        tv_show_id = TVShows.query.filter_by(title=title).first().id

        for genre_id in genre_ids:
            tv_show_genre = TVShowGenre(
                tv_show_id=tv_show_id,
                genre_id=genre_id
            )
            db.session.add(tv_show_genre)
        db.session.commit()
        return jsonify({'success': success_check,
                        'valid_title': title_check,
                        'valid_year': year_check,
                        'valid_service': service_check,
                        'valid_tag': tag_check,
                        'valid_url': url_check,
                        'valid_num_episodes': num_episodes_check,
                        'valid_num_seasons': num_seasons_check,
                        'valid image_url': image_url_check,
                        'valid_genre_type': genre_type_check,
                        'valid_description': description_check, })
    except Exception as e:
        return str(e)


# [url]/tv_shows/title=[title]/info
@app.route('/tv_shows/title=<title>/info', methods=['GET'])
@app.route('/tv_shows/title=/info', methods=['GET'])
def get_tv_show_info(title=None):
    tv_info = list()

    if title is not None:
        tv_show = TVShows.query.filter_by(title=title).first()
        if tv_show is not None:
            tv_show_id = tv_show.id
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

                entry = TVShowSeasonInfo(season_id, episodes)
                tv_info.append(entry)

            # Display Every Season
            return jsonify({title: [tvi.serialize() for tvi in tv_info]})

    return jsonify({'title': tv_info})


# [url/tv_shows/recently_added
@app.route('/tv_shows/recently_added/page=<page>', methods=['GET'])
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
@app.route('/tv_shows/title=<title>/page=<page>', methods=['GET'])
@app.route('/tv_shows/title=<title>', methods=['GET'])
@app.route('/tv_shows/title=', methods=['GET'])
def get_tv_shows_by_title(title=None, search_all=False, page=1):
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


# Query TV Shows by Service Provider
# [url]/tv_shows/service=[service_provider]
@app.route('/tv_shows/service=<service>/page=<page>', methods=['GET'])
@app.route('/tv_shows/service=<service>', methods=['GET'])
@app.route('/tv_shows/service=', methods=['GET'])
def get_tv_shows_by_service(service=None, search_all=False, page=1):
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


# Query TV Shows by Genre Type
# [url]/tv_shows/genre=[genre_type]
@app.route('/tv_shows/genre=<genre>/page=<page>', methods=['GET'])
@app.route('/tv_shows/genre=<genre>', methods=['GET'])
@app.route('/tv_shows/genre=', methods=['GET'])
def get_tv_shows_by_genre(genre=None, search_all=False, page=1):
    tv_shows = list()

    if genre is not None:
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

    return paginated_json('tv_shows', tv_shows, page)


# Query TV Shows by Years Running
# [url]/tv_shows/year=[year]
@app.route('/tv_shows/year=<year>/page=<page>', methods=['GET'])
@app.route('/tv_shows/year=<year>', methods=['GET'])
@app.route('/tv_shows/year=', methods=['GET'])
def get_tv_shows_by_year(year=None, search_all=False, page=1):
    tv_shows = list()

    if year is not None and year.isdigit():
        queried_year = year

        # Get list of all TVShows
        all_tv_shows = TVShows.query.all()

        for tv_show in all_tv_shows:
            tv_show_year = tv_show.year
            years_running = list()

            # Show Ran for One Year
            if len(tv_show_year) == 4:
                if tv_show_year == queried_year:
                    years_running.append(tv_show_year)

            # Ongoing Show
            elif tv_show_year[-1] == '-':
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

    # return json of queried movies

    if search_all:
        return tv_shows
    else:
        return paginated_json('tv_shows', tv_shows, page)


# [url]/tv_shows/actor=[actor_full_name]/page=[page]
# [url]/tv_shows/actor=[actor_full_name]
@app.route('/tv_shows/actor=<actor_name>/page=<page>', methods=['GET'])
@app.route('/tv_shows/actor=<actor_name>', methods=['GET'])
@app.route('/tv_shows/actor=', methods=['GET'])
def get_tv_shows_by_actor(actor_name=None, search_all=False, page=1):
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


# Return a list of tv_shows that match query in any column
@app.route('/tv_shows/all=<query>/page=<page>', methods=['GET'])
@app.route('/tv_shows/all=<query>', methods=['GET'])
@app.route('/tv_shows/all=', methods=['GET'])
def get_tv_shows_search_all(query=None, search_all=False, page=1):
    tv_shows = list()

    if query is not None:

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

    return paginated_json('tv_shows', tv_shows, page)


# Search All Route
# [url]/all=[query]
@app.route('/all=<query>/page=<page>', methods=['GET'])
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


# Individual Movie Info
def movie_info(title):
    try:
        movie = Movie.query.filter_by(title=title).first()
        movie_actors = ActorMovie.query.filter_by(movie_id=movie.id).all()
        movie_genres = MovieGenre.query.filter_by(movie_id=movie.id).all()

        # Get list of all stars in tv show
        stars = list()
        if movie_actors is None:
            stars = None
        else:
            # For each actor
            for ma in movie_actors:
                actor = Actor.query.filter_by(id=ma.actor_id).first()
                stars.append(actor.full_name)

        # Gets list of all genres in tv show
        genres = list()
        if movie_genres is None:
            genres = None
        else:
            # For each genre
            for mg in movie_genres:
                genre = Genre.query.filter_by(id=mg.genre_id).first()
                genres.append(genre.genre_type)

        if movie is not None:
            movie_id = movie.id
            title = movie.title
            year = movie.year
            url = movie.url
            description = movie.description
            image_url = movie.image_url
            avg_rating = movie.avg_rating

            movie_info = MovieInfo(movie_id, title, year, url, description, stars, genres, image_url, avg_rating)
            return movie_info

        return None
    except Exception as e:
        return str(e)


# Individual TV Show Info
def tv_show_info(title):
    try:
        tv_season_info = list()

        tv_show = TVShows.query.filter_by(title=title).first()
        tv_show_id = tv_show.id
        tv_show_actors = ActorsTVShow.query.filter_by(tv_show_id=tv_show_id).all()
        tv_show_genres = TVShowGenre.query.filter_by(tv_show_id=tv_show_id).all()

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

                entry = TVShowSeasonInfo(season_id, episodes)
                tv_season_info.append(entry)

            # Get list of all stars in tv show
            stars = list()
            if tv_show_actors is None:
                stars = None
            else:
                # For each actor
                for tsa in tv_show_actors:
                    actor = Actor.query.filter_by(id=tsa.actors_id).first()
                    stars.append(actor.full_name)

            # Gets list of all genres in tv show
            genres = list()
            if tv_show_genres is None:
                genres = None
            else:
                # For each genre
                for tsg in tv_show_genres:
                    genre = Genre.query.filter_by(id=tsg.genre_id).first()
                    genres.append(genre.genre_type)

            # Convert to TV Show Info
            title = tv_show.title
            year = tv_show.year
            description = tv_show.description
            image_url = tv_show.image_url
            avg_rating = tv_show.avg_rating

            tv_show_info = TVShowInfo(tv_show_id, title, year, description, stars, genres, tv_season_info, image_url,
                                      avg_rating)
            return tv_show_info
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
