#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from distutils.log import error
import json
import dateutil.parser
import babel
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
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
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
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
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres =  db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
    artist_shows = db.relationship('Show', backref = 'artist_show')

class Show(db.Model):
   __tablename__ = 'Show'

   id = db.Column(db.Integer, primary_key=True)
   venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
   artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
   start_time = db.Column(db.DateTime)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  rows = db.session.query(Venue.city, Venue.state).distinct().all()
  data = []
  for row in rows:
      dict = {}
      dict['city'] = row.city.strip()
      dict['state'] = row.state.strip()
      dict['venues'] = []

      venues = db.session.query(Venue).filter_by(city = row.city, state = row.state).all()
      print(venues)
      for venue in venues:
          venue_dict = {}
          venue_dict['id'] = venue.id
          venue_dict['name'] = venue.name
          shows_count = db.session.query(Show).filter_by(venue_id = str(venue.id)).count()
          venue_dict['num_upcoming_shows'] = shows_count
          dict['venues'].append(venue_dict)
      data.append(dict)
   
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_for = request.form['search_term']
  response = {}
  rows = db.session.query(Venue).filter(Venue.name.ilike('%'+search_for+'%')).all()
  response['count']= len(rows)
  response['data'] = []
  for row in rows:
    dict = {}
    dict['id'] = row.id
    dict['name'] = row.name
    shows_count = db.session.query(Show).filter_by(venue_id = str(row.id)).count()
    dict['num_upcoming_shows'] = shows_count
    response['data'].append(dict)
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = {}
  row = db.session.query(Venue).filter_by(id=int(venue_id)).all()
  for venue in row:
    print(venue.genres)
    data['id'] = venue.id
    data['name'] = venue.name.strip()
    data['genres'] = venue.genres.replace("{", "").replace("}", "").replace('"', "").split(',')
    data['address'] = venue.address.strip()
    data['city'] = venue.city.strip()
    data['state'] = venue.state.strip()
    data['phone'] = venue.phone.strip()
    data['website'] = venue.website_link.strip()
    data['facebook_link'] = venue.facebook_link.strip()
    data['seeking_talent'] = venue.seeking_talent
    data['seeking_description'] = venue.seeking_description.strip()
    data['image_link'] = venue.image_link.strip()
    data['past_shows'] = [] 
    data['upcoming_shows'] = []
    datenow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    past_shows = db.session.query(Show).filter(Show.venue_id == str(venue.id)).filter(Show.start_time <= datenow).all()
    upcoming_shows = db.session.query(Show).filter(Show.venue_id == str(venue.id)).filter(Show.start_time > datenow).all()
    for past_show in past_shows:
        dict_past = {}
        dict_past['artist_id'] = past_show.artist_id
        dict_past['start_time'] = past_show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        artists = db.session.query(Artist).filter_by(id=past_show.artist_id)
        for artist in artists:
          dict_past['artist_name'] = artist.name.strip()
          dict_past['artist_image_link'] = artist.image_link
        data['past_shows'].append(dict_past)    
    for upcoming_show in upcoming_shows:
        dict_upcoming = {}
        dict_upcoming['artist_id'] = upcoming_show.artist_id.strip()
        dict_upcoming['start_time'] = upcoming_show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        artists = db.session.query(Artist).filter_by(id=upcoming_show.artist_id)
        for artist in artists:
          dict_upcoming['artist_name'] = artist.name.strip()
          dict_upcoming['artist_image_link'] = artist.image_link.strip()
        data['upcoming_shows'].append(dict_upcoming)          
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()
  if form.seeking_talent.data:
      seeking_talent = True
  else:
      seeking_talent = False
  venue = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      image_link = form.image_link.data,
      website_link = form.website_link.data,
      seeking_talent = seeking_talent,
      seeking_description = form.seeking_description.data
    )
  # Add venue to db
  try: 
    db.session.add(venue)
    db.session.commit()
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except:
    flash('Venue ' + request.form['name'] + ' could not be added. Please try again!')
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
     db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.    
  venue = Venue.query.get(int(venue_id))
  deleted = False
  message = ''
  try:
        db.session.delete(venue)
        db.session.commit()
        deleted = True
        message = 'Venue deleted successfully'
  except:
        message = 'Could not delete the Venue. Please try again!!'
  finally:
          db.session.close()       
  return jsonify({'deleted' : deleted, 'message': message})          
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artists = db.session.query(Artist).with_entities(Artist.id, Artist.name).all();
  for artist in artists:
      dict = {}
      dict['id'] = artist.id
      dict['name'] = artist.name
      data.append(dict)
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_for = request.form['search_term']
  response = {}
  rows = db.session.query(Artist).filter(Artist.name.ilike('%'+search_for+'%')).all()
  response['count']= len(rows)
  response['data'] = []
  for row in rows:
    dict = {}
    dict['id'] = row.id
    dict['name'] = row.name
    shows_count = db.session.query(Show).filter_by(venue_id = str(row.id)).count()
    dict['num_upcoming_shows'] = shows_count
    response['data'].append(dict)
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data = {}
  row = db.session.query(Artist).filter_by(id=int(artist_id)).all()
  for artist in row:
    data['id'] = artist.id
    data['name'] = artist.name.strip()
    data['genres'] = artist.genres.replace("{", "").replace("}", "").replace('"', "").split(',')
    data['city'] = artist.city.strip()
    data['state'] = artist.state.strip()
    data['phone'] = artist.phone.strip()
    data['website'] = artist.website_link.strip()
    data['facebook_link'] = artist.facebook_link.strip()
    data['seeking_venue'] = artist.seeking_venue
    data['seeking_description'] = artist.seeking_description.strip()
    data['image_link'] = artist.image_link.strip()
    data['past_shows'] = [] 
    data['upcoming_shows'] = []
    datenow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    past_shows = db.session.query(Show).filter(Show.artist_id == str(artist.id)).filter(Show.start_time <= datenow).all()
    upcoming_shows = db.session.query(Show).filter(Show.artist_id == str(artist.id)).filter(Show.start_time > datenow).all()
    for past_show in past_shows:
        dict_past = {}
        dict_past['venue_id'] = past_show.venue_id
        dict_past['start_time'] = past_show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        venues = db.session.query(Venue).filter(Venue.id==past_show.venue_id)
        for venue in venues:
          dict_past['venue_name'] = venue.name.strip()
          dict_past['venue_image_link'] = venue.image_link.strip()
        data['past_shows'].append(dict_past)    
    for upcoming_show in upcoming_shows:
        dict_upcoming = {}
        dict_upcoming['venue_id'] = upcoming_show.venue_id.strip()
        dict_upcoming['start_time'] = upcoming_show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        venues = db.session.query(Venue).filter(Venue.id==upcoming_show.venue_id)
        for venue in venues:
          dict_upcoming['venue_id_name'] = venue.name.strip()
          dict_upcoming['venue_image_link'] = venue.image_link.strip()
        data['upcoming_shows'].append(dict_upcoming)          
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = {}
  row = Artist.query.get(artist_id)
  artist['id'] = row.id
  artist['name'] = row.name
  artist['genres'] = row.genres
  artist['city'] = row.city
  artist['state'] = row.state
  artist['phone'] = row.phone
  artist['website'] = row.website_link
  artist['facebook_link'] = row.facebook_link
  artist['seeking_venue'] = row.seeking_venue
  artist['seeking_description'] = row.seeking_description
  artist['image_link'] = row.image_link
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form= ArtistForm()
  artist = Artist.query.get(artist_id)
  #find changes
  if form.name.data != artist.name:
     artist.name=form.name.data
  if form.city.data != artist.city:
    artist.city=form.city.data
  if form.state.data != artist.state:
    artist.state=form.state.data
  if form.phone.data != artist.phone:
    artist.phone=form.phone.data
  if form.image_link.data != artist.image_link:
    artist.image_link=form.image_link.data
  if form.facebook_link.data != artist.facebook_link:
    artist.facebook_link=form.facebook_link.data
  if form.website_link.data != artist.website_link:
    artist.website_link=form.website_link.data
  if form.seeking_venue.data != artist.seeking_venue:
    artist.seeking_venue=form.seeking_venue.data
  if form.seeking_description.data != artist.seeking_description:
    artist.seeking_description=form.seeking_description.data
  if form.genres.data != artist.genres: 
    artist.genres=form.genres.data       
  db.session.commit()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = {}
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  row = db.session.query(Venue).filter_by(id=int(venue_id))
  for data in row:
      venue['id'] = data.id
      venue['name'] = data.name
      venue['genres'] = data.genres
      venue['address'] = data.address
      venue['city'] = data.city
      venue['state'] = data.state
      venue['phone'] = data.phone
      venue['website'] = data.website_link
      venue['facebook_link'] = data.facebook_link
      venue['seeking_talent'] = data.seeking_talent
      venue['seeking_description'] = data.seeking_description
      venue['image_link'] = data.image_link
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  #find changes
  if form.name.data != venue.name:
     venue.name=form.name.data
  if form.city.data != venue.city:
    venue.city=form.city.data
  if form.state.data != venue.state:
    venue.state=form.state.data
  if form.address.data != venue.address:
    venue.address=form.address.data
  if form.phone.data != venue.phone:
    venue.phone=form.phone.data
  if form.image_link.data != venue.image_link:
    venue.image_link=form.image_link.data
  if form.facebook_link.data != venue.facebook_link:
    venue.facebook_link=form.facebook_link.data
  if form.website_link.data != venue.website_link:
    venue.website_link=form.website_link.data
  if form.seeking_talent.data != venue.seeking_talent:
    venue.seeking_talent=form.seeking_talent.data
  if form.seeking_description.data != venue.seeking_description:
    venue.seeking_description=form.seeking_description.data
  if form.genres.data != venue.genres: 
    venue.genres=form.genres.data       
  db.session.commit()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm() 
  if form.seeking_venue.data:
      seeking_venue = True
  else:
      seeking_venue = False
  artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      image_link = form.image_link.data,
      website_link = form.website_link.data,
      seeking_venue = seeking_venue,
      seeking_description = form.seeking_description.data
    )
  # Add artist to db
  try: 
      db.session.add(artist)
      db.session.commit()
  # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  except:
      flash('Artist ' + request.form['name'] + ' could not be added. Please try again!')
  finally:
     db.session.close()  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = Show.query.all()
  for show in shows:
    dict = {}
    dict['venue_id'] = show.venue_id
    dict['artist_id'] = show.artist_id
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)
    dict['venue_name'] = venue.name
    dict['artist_name'] = artist.name
    dict['artist_image_link'] = artist.image_link
    dict['start_time'] = show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    data.append(dict)
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form= ShowForm()
  valid_artist = db.session.get(Artist, form.artist_id.data) 
  valid_venue = db.session.get(Venue, form.venue_id.data)
  start_time=form.start_time.data.strftime("%Y-%m-%d %H:%M:%S")
  if valid_artist == None and valid_venue == None:
     error_message = 'Invalid Artist and Venue name! Please enter valid values'
  elif valid_venue == None:
     error_message = 'Invalid Venue name! Please enter valid value'
  elif valid_artist == None:
     error_message =  'Invalid Artist name! Please enter valid value' 
  else:
     error_message =  None
  if  error_message == None:  
   #Add Show to Db
    show = Show(
     artist_id = form.artist_id.data,
     venue_id = form.venue_id.data,
     start_time = start_time
   )
    try: 
      db.session.add(show)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except:
      flash('Show could not be added. Please try again!')
    finally:
       db.session.close() 
  else:
   flash(error_message)        
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
