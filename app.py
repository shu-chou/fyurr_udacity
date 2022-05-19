#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import (jsonify, 
render_template, 
request, 
Response, 
flash, 
redirect, 
url_for)
import logging
from logging import Formatter, FileHandler
from sqlalchemy import func
from forms import *
from models import *

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
  # This route lists all the venues
  rows = db.session.query(Venue.city, Venue.state).distinct().all()
  data = []
  for row in rows:
      dict = {}
      dict['city'] = row.city.strip()
      dict['state'] = row.state.strip()
      dict['venues'] = []

      venues = db.session.query(Venue.id, Venue.name, func.count(Show.id) ).\
              join(Show).filter(Venue.city ==row.city).\
              filter(Venue.state == row.state).\
              group_by(Venue.id).all()
      print(venues)
      for venue in venues:
        
          venue_dict = {}
          venue_dict['id'] = venue[0]
          venue_dict['name'] = venue[1]
          venue_dict['num_upcoming_shows'] = venue[2]
          dict['venues'].append(venue_dict)
      data.append(dict)
   

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
#This route help search venuew
  search_for = request.form['search_term']
  response = {}
  rows = db.session.query(Venue).filter(Venue.name.ilike('%'+search_for+'%')).all()
  response['count']= len(rows)
  response['data'] = []
  for row in rows:
    dict = {}
    dict['id'] = row.id
    dict['name'] = row.name
    shows_count = db.session.query(Venue).join(Show).filter(Show.venue_id == str(row.id)).\
      filter(Show.start_time > datetime.now().strftime("%Y-%m-%d %H:%M:%S")).\
      count()
    dict['num_upcoming_shows'] = shows_count
    response['data'].append(dict)
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # This route lists the venues based on their id
  data = {}
  row = db.session.query(Venue).filter_by(id=int(venue_id)).all()
  for venue in row:
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
    past_shows = db.session.query(Venue.id, Show.id, Show.artist_id, Show.start_time).join(Show).filter(Show.venue_id == str(venue.id)).\
                 filter(Show.start_time <= datenow).all()
    upcoming_shows = db.session.query(Venue.id, Show.id, Show.artist_id, Show.start_time).join(Show).filter(Show.venue_id == str(venue.id)).\
                 filter(Show.start_time > datenow).all()
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
        dict_upcoming['artist_id'] = upcoming_show.artist_id
        dict_upcoming['start_time'] = upcoming_show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        artists = db.session.query(Artist).filter_by(id=upcoming_show.artist_id)
        for artist in artists:
          dict_upcoming['artist_name'] = artist.name.strip()
          dict_upcoming['artist_image_link'] = artist.image_link.strip()
        data['upcoming_shows'].append(dict_upcoming)          
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  #This route is used to create a new venue
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
  # on unsuccessful db insert, flash an error instead.
  except:
    flash('Venue ' + request.form['name'] + ' could not be added. Please try again!')
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
     db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # Thia route delete a specific venue  
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
  # This route lists all the artists
  data = []
  artists = db.session.query(Artist).with_entities(Artist.id, Artist.name).all();
  for artist in artists:
      dict = {}
      dict['id'] = artist.id
      dict['name'] = artist.name
      data.append(dict)
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # This route help search artists
  search_for = request.form['search_term']
  response = {}
  rows = db.session.query(Artist).filter(Artist.name.ilike('%'+search_for+'%')).all()
  response['count']= len(rows)
  response['data'] = []
  for row in rows:
    dict = {}
    dict['id'] = row.id
    dict['name'] = row.name
    shows_count = db.session.query(Artist).join(Show).filter(Show.artist_id == str(row.id)).count()
    dict['num_upcoming_shows'] = shows_count
    response['data'].append(dict)
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # This route list artist based on their id
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
    past_shows = db.session.query(Artist.id, Show.venue_id, Show.start_time).join(Show).filter(Show.artist_id == str(artist.id)).\
                 filter(Show.start_time <= datenow).all()
    upcoming_shows = db.session.query(Artist.id, Show.venue_id, Show.start_time).join(Show).filter(Show.artist_id == str(artist.id)).\
                     filter(Show.start_time > datenow).all()
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
        dict_upcoming['venue_id'] = upcoming_show.venue_id
        dict_upcoming['start_time'] = upcoming_show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        venues = db.session.query(Venue).filter(Venue.id==upcoming_show.venue_id)
        for venue in venues:
          dict_upcoming['venue_id_name'] = venue.name.strip()
          dict_upcoming['venue_image_link'] = venue.image_link.strip()
        data['upcoming_shows'].append(dict_upcoming)          
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
# This route edit artist based on their id
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

  #  populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # This route edit artist based on their id
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
  
  #  populate form with values from venue with ID <venue_id>
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
 # This route edit venue based on their id
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
  # This route create new artist 
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
  #  on unsuccessful db insert, flash an error instead.
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
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # This route create new show
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
  # on unsuccessful db insert, flash an error instead.

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
