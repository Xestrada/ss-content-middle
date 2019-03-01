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
