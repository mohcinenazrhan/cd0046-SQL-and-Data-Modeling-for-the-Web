#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from forms import *
from sqlalchemy.exc import SQLAlchemyError
from models import db_setup, Venue, Show, Artist

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
db = db_setup(app)

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
  
  current_time = datetime.now()
  venues = Venue.query.order_by(Venue.city, Venue.state).all()
  venue_state_and_city = ''
  data = []

  for venue in venues:
    num_upcoming_shows = len(venue.shows.filter(Show.start_time > current_time).all())

    if venue_state_and_city == venue.state + venue.city:
      data[len(data) - 1]["venues"].append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows
      })
    else:
      data.append({
        "city": venue.city,
        "state": venue.state,
        "venues": [{
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": num_upcoming_shows
        }]
      })
      venue_state_and_city = venue.state + venue.city

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term = request.form.get('search_term', '')
  venue_query = Venue.query.filter(Venue.name.ilike('%' + search_term + '%'))

  venue_list = list(map(Venue.names, venue_query)) 

  response = {
    "count": len(venue_list),
    "data": venue_list
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
  current_time = datetime.now()
  venue = Venue.query.get(venue_id)

  venue_details = Venue.detail(venue)
  upcoming_shows = Show.query.options(db.joinedload(Show.venue)).filter(Show.venue_id == venue_id).filter(Show.start_time > current_time).all()
  past_shows = Show.query.options(db.joinedload(Show.venue)).filter(Show.venue_id == venue_id).filter(Show.start_time <= current_time).all()

  venue_details['past_shows'] = list(map(Show.artist_details, past_shows))
  venue_details['upcoming_shows'] = list(map(Show.artist_details, upcoming_shows))
  venue_details['past_shows_count'] = len(past_shows)
  venue_details['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=venue_details)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  form = VenueForm(request.form)
  if form.validate():

    try:
      seeking_talent = False
      seeking_description = ''
      if 'seeking_talent' in request.form:
        seeking_talent = request.form['seeking_talent'] == 'y'
      if 'seeking_description' in request.form:
        seeking_description = request.form['seeking_description']

      new_venue = Venue(
        name = request.form['name'],
        genres = ','.join(request.form.getlist('genres')),
        address = request.form['address'],
        city = request.form['city'],
        state = request.form['state'],
        phone = request.form['phone'],
        website = request.form['website_link'],
        facebook_link = request.form['facebook_link'],
        image_link = request.form['image_link'],
        seeking_talent = seeking_talent,
        seeking_description = seeking_description,
      )

      Venue.insert(new_venue)
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except SQLAlchemyError as e:
      print('except ' + e)
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()

  else:
    print(form.errors)
    flash('Invalid inputs.')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()

  if error:
    abort(500)
  else:
    return jsonify({'success' : True})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  artists = list(map(Artist.names, Artist.query.order_by(Artist.name).all()))

  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term = request.form.get('search_term', '')
  artist_query = Artist.query.filter(Artist.name.ilike('%' + search_term + '%'))

  artist_list = list(map(Artist.names, artist_query))

  response = {
    "count" : len(artist_list),
    "data" : artist_list
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  current_time = datetime.now()
  artist = Artist.query.get(artist_id)

  artist_details = Artist.detail(artist)
  upcoming_shows = Show.query.options(db.joinedload(Show.venue)).filter(Show.venue_id == artist_id).filter(Show.start_time > current_time).all()
  past_shows = Show.query.options(db.joinedload(Show.venue)).filter(Show.venue_id == artist_id).filter(Show.start_time <= current_time).all()

  artist_details['past_shows'] = list(map(Show.venue_details, past_shows))
  artist_details['upcoming_shows'] = list(map(Show.venue_details, upcoming_shows))
  artist_details['past_shows_count'] = len(past_shows)
  artist_details['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_artist.html', artist=artist_details)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website_link.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  form = ArtistForm(request.form)
  artist_data = Artist.query.get(artist_id)

  if form.validate():
    seeking_venue = False
    seeking_description = ''

    if 'seeking_venue' in request.form:
        seeking_venue = request.form['seeking_venue'] == 'y'
    if 'seeking_description' in request.form:
        seeking_description = request.form['seeking_description']

    setattr(artist_data, 'name', request.form['name'])
    setattr(artist_data, 'genres', ','.join(request.form.getlist('genres')))
    setattr(artist_data, 'city', request.form['city'])
    setattr(artist_data, 'state', request.form['state'])
    setattr(artist_data, 'phone', request.form['phone'])
    setattr(artist_data, 'website', request.form['website_link'])
    setattr(artist_data, 'facebook_link', request.form['facebook_link'])
    setattr(artist_data, 'image_link', request.form['image_link'])
    setattr(artist_data, 'seeking_description', seeking_description)
    setattr(artist_data, 'seeking_venue', seeking_venue)

    Artist.update(artist_data)
  else:
    flash('Invalid inputs.')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  form = VenueForm()
  venue = Venue.query.get(venue_id)

  form.name.data = venue.name
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website_link.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  form = VenueForm(request.form)
  venue_data = Venue.query.get(venue_id)

  if form.validate():
    seeking_talent = False
    seeking_description = ''

    if 'seeking_talent' in request.form:
        seeking_talent = request.form['seeking_talent'] == 'y'
    if 'seeking_description' in request.form:
        seeking_description = request.form['seeking_description']

    setattr(venue_data, 'name', request.form['name'])
    setattr(venue_data, 'genres', ','.join(request.form.getlist('genres')))
    setattr(venue_data, 'address', request.form['address'])
    setattr(venue_data, 'city', request.form['city'])
    setattr(venue_data, 'state', request.form['state'])
    setattr(venue_data, 'phone', request.form['phone'])
    setattr(venue_data, 'website', request.form['website_link'])
    setattr(venue_data, 'facebook_link', request.form['facebook_link'])
    setattr(venue_data, 'image_link', request.form['image_link'])
    setattr(venue_data, 'seeking_description', seeking_description)
    setattr(venue_data, 'seeking_talent', seeking_talent)

    Venue.update(venue_data)
  else:
    flash('Invalid inputs.')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  form = ArtistForm(request.form)
  if form.validate():

    try:
      seeking_venue = False
      seeking_description = ''
      if 'seeking_venue' in request.form:
        seeking_venue = request.form['seeking_venue'] == 'y'
      if 'seeking_description' in request.form:
        seeking_description = request.form['seeking_description']

      new_artist = Artist(
        name = request.form['name'],
        genres = ','.join(request.form.getlist('genres')),
        address = request.form['address'],
        city = request.form['city'],
        state = request.form['state'],
        phone = request.form['phone'],
        website = request.form['website_link'],
        facebook_link = request.form['facebook_link'],
        image_link = request.form['image_link'],
        seeking_venue = seeking_venue,
        seeking_description = seeking_description,
      )

      Venue.insert(new_artist)
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except SQLAlchemyError as e:
      print('except ' + e)
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()

  else:
    print(form.errors)
    flash('Invalid inputs.')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  shows = list(map(Show.detail, Show.query.order_by(Show.start_time).all()))

  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  try:
    new_show = Show(
      venue_id = request.form['venue_id'],
      artist_id = request.form['artist_id'],
      start_time = request.form['start_time'],
    )

    Show.insert(new_show)

    flash('Show was successfully listed!')
  except:
    flash('An error occured. Show could not be listed.')

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
