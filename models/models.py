from app import db


class Actor(db.Model):
    __tablename__ = 'actors'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.VARCHAR)
    first_name = db.Column(db.VARCHAR)
    last_name = db.Column(db.VARCHAR)

    def serialize(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
        }


class ActorMovie(db.Model):
    __tablename__ = 'movie_actors'

    movie_id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, primary_key=True)


class ActorsTVShow(db.Model):
    __tablename__ = 'tv_show_actors'

    tv_show_id = db.Column(db.Integer, primary_key=True)
    actors_id = db.Column(db.Integer, primary_key=True)
