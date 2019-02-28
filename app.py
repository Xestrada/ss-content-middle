from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pymysql
import os

#Setup App
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS']) #Should change based on is in Development or Production
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS
CORS(app)

#Start Database
db = SQLAlchemy(app)

# Enable Variable port for Heroku
port = int(os.environ.get('PORT', 33507))

#Import models
from models import Actor

# Force pymysql to be used as replacement for MySQLdb
pymysql.install_as_MySQLdb()

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/actors', methods=['GET'])
def actors():
    actors = Actor.query.all()
    return jsonify({'actors': actor.serialize() for actor in actors})



if __name__ == '__main__':
    app.run(port=port)
