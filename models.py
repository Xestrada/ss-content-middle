from app import db


class Actor(db.Model):
    __tablename__ = 'actors'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.VARCHAR)
    first_name = db.Column(db.VARCHAR)
    last_name = db.Column(db.VARCHAR)
    movie_list = db.Column(db.VARCHAR)

    def __init__(self, full_name, first_name, last_name, movie_list):
        self.full_name = full_name
        self.first_name = first_name
        self.last_name = last_name
        self.movie_list = movie_list

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'movie_list': self.movie_list,
        }


class Movie(db.Model):
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.VARCHAR)
    year = db.Column(db.VARCHAR)
    service = db.Column(db.VARCHAR)
    tag = db.Column(db.VARCHAR)
    url = db.Column(db.VARCHAR)

    def __init__(self, title, year, service, tag, url):
        self.title = title
        self.year = year
        self.service = service
        self.tag = tag
        self.url = url

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'year': self.year,
            'service': self.service,
            'tag': self.tag,
            'url': self.url,
        }


class TV_Shows(db.Model):
    __tablename__ = 'tv_shows'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.VARCHAR)
    year = db.Column(db.VARCHAR)
    num_seasons = db.Column(db.INTEGER)
    num_episodes = db.Column(db.INTEGER)
    service = db.Column(db.VARCHAR)
    tag = db.Column(db.VARCHAR)
    url = db.Column(db.VARCHAR)

    def __init__(self, title, year, num_seasons, num_episodes, service, tag, url):
        self.title = title
        self.year = year
        self.num_seasons = num_seasons
        self.num_episodes = num_episodes
        self.service = service
        self.tag = tag
        self.url = url

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'year': self.year,
            'num_seasons': self.num_seasons,
            'num_episodes': self.num_episodes,
            'service': self.service,
            'tag': self.tag,
            'url': self.url,
        }

