
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

#connect to a local postgresql database

def db_setup(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    Migrate(app, db)
    return db

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = "shows"
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id"), primary_key=True)
    start_time = db.Column(db.DateTime)

    def insert(self):
      db.session.add(self)
      db.session.commit()
      
    def detail(self):
      return{
          'venue_id' : self.venue_id,
          'venue_name' : self.venue.name,
          'artist_id' : self.artist_id,
          'artist_name' : self.artist.name,
          'artist_image_link' : self.artist.image_link,
          'start_time' : self.start_time.strftime('%Y-%m-%d %H:%M:%S')
      }

    def artist_details(self):
      return {
          'artist_id' : self.venue_id,
          'artist_name' : self.artist.name,
          'artist_image_link' : self.artist.image_link,
          'start_time' : self.start_time.strftime('%Y-%m-%d %H:%M:%S')
      }

    def venue_details(self):
      return {
          'venue_id' : self.venue_id,
          'venue_name' : self.venue.name,
          'venue_image_link' : self.venue.image_link,
          'start_time' : self.start_time.strftime('%Y-%m-%d %H:%M:%S')
      }

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120), default='')
    shows = db.relationship("Show", lazy='dynamic', backref='venue')

    def insert(self):
      db.session.add(self)
      db.session.commit()

    def update(self):
      db.session.commit()
    
    def names(self):
      return{
          'id' : self.id,
          'name' : self.name,
          'num_upcoming_shows' : len(self.shows.filter(Show.start_time > datetime.now()).all()), 
      }

    def detail(self):
      return{
          'id' : self.id,
          'name' : self.name,
          'genres' : self.genres.split(","),
          'address' : self.address,
          'city' : self.city,
          'phone' : self.phone,
          'website' : self.website,
          'facebook_link' : self.facebook_link,
          'seeking_talent' : self.seeking_talent,
          'seeking_description' : self.seeking_description,
          'image_link' : self.image_link
      }

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120), default='')
    shows = db.relationship("Show", lazy='dynamic', backref='artist')

    def update(self):
      db.session.commit()

    def names(self):
      return {
        'id' : self.id,
        'name' : self.name,
        'num_upcoming_shows' : len(self.shows.filter(Show.start_time > datetime.now()).all()), 
      }

    def detail(self):
      return {
        'id' : self.id,
        'name' : self.name,
        'genres' : self.genres.split(","),
        'city' : self.city,
        'state' : self.state,
        'phone' : self.phone,
        'website' : self.website,
        'facebook_link' : self.facebook_link,
        'seeking_venue' : self.seeking_venue,
        'seeking_description' : self.seeking_description,
        'image_link' : self.image_link,
      }