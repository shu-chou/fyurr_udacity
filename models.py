#----------------------------------------------------------------------------#
# Database configuration, models and relationships
#----------------------------------------------------------------------------#
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from flask import Flask
from config import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
# DB Migration
migrate = Migrate(app, db)
# connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = DatabaseURI.SQLALCHEMY_DATABASE_URI


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    venue_shows = db.relationship('Show', backref = 'venue_show')

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres =  db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    
# Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
    artist_shows = db.relationship('Show', backref = 'artist_show')

class Show(db.Model):
   __tablename__ = 'Show'

   id = db.Column(db.Integer, primary_key=True)
   venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
   artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
   start_time = db.Column(db.DateTime)