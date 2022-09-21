from datetime import datetime
import re
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, ValidationError
from wtforms.validators import DataRequired, AnyOf, URL, Length, Optional

state_choices = [
    ('AL', 'AL'),
    ('AK', 'AK'),
    ('AZ', 'AZ'),
    ('AR', 'AR'),
    ('CA', 'CA'),
    ('CO', 'CO'),
    ('CT', 'CT'),
    ('DE', 'DE'),
    ('DC', 'DC'),
    ('FL', 'FL'),
    ('GA', 'GA'),
    ('HI', 'HI'),
    ('ID', 'ID'),
    ('IL', 'IL'),
    ('IN', 'IN'),
    ('IA', 'IA'),
    ('KS', 'KS'),
    ('KY', 'KY'),
    ('LA', 'LA'),
    ('ME', 'ME'),
    ('MT', 'MT'),
    ('NE', 'NE'),
    ('NV', 'NV'),
    ('NH', 'NH'),
    ('NJ', 'NJ'),
    ('NM', 'NM'),
    ('NY', 'NY'),
    ('NC', 'NC'),
    ('ND', 'ND'),
    ('OH', 'OH'),
    ('OK', 'OK'),
    ('OR', 'OR'),
    ('MD', 'MD'),
    ('MA', 'MA'),
    ('MI', 'MI'),
    ('MN', 'MN'),
    ('MS', 'MS'),
    ('MO', 'MO'),
    ('PA', 'PA'),
    ('RI', 'RI'),
    ('SC', 'SC'),
    ('SD', 'SD'),
    ('TN', 'TN'),
    ('TX', 'TX'),
    ('UT', 'UT'),
    ('VT', 'VT'),
    ('VA', 'VA'),
    ('WA', 'WA'),
    ('WV', 'WV'),
    ('WI', 'WI'),
    ('WY', 'WY'),
]

genres_choices = [
    ('Alternative', 'Alternative'),
    ('Blues', 'Blues'),
    ('Classical', 'Classical'),
    ('Country', 'Country'),
    ('Electronic', 'Electronic'),
    ('Folk', 'Folk'),
    ('Funk', 'Funk'),
    ('Hip-Hop', 'Hip-Hop'),
    ('Heavy Metal', 'Heavy Metal'),
    ('Instrumental', 'Instrumental'),
    ('Jazz', 'Jazz'),
    ('Musical Theatre', 'Musical Theatre'),
    ('Pop', 'Pop'),
    ('Punk', 'Punk'),
    ('R&B', 'R&B'),
    ('Reggae', 'Reggae'),
    ('Rock n Roll', 'Rock n Roll'),
    ('Soul', 'Soul'),
    ('Other', 'Other'),
]

def phone_validator(val):
    if not re.search(r"^[0-9]{3}-[0-9]{3}-[0-9]{4}$", val):
        raise ValidationError("Invalid phone number.")

def genres_validator(val):
    genres_values = [choice[1] for choice in genres_choices]
    for value in val:
        if value not in genres_values:
            raise ValidationError('Invalid genres value.')

class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(Form):
    def validate_phone(form, field):
        phone_validator(field.data)

    def validate_genres(form, field):
        genres_validator(field.data)
            
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices = state_choices
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone', validators=[Optional()]
    )
    image_link = StringField(
        'image_link', validators=[Optional(), URL(), Length(max=500)]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices = genres_choices
    )
    facebook_link = StringField(
        'facebook_link', validators=[Optional(), URL(), Length(max=120)]
    )
    website_link = StringField(
        'website_link', validators=[Optional(), URL(), Length(max=120)]
    )

    seeking_talent = BooleanField( 'seeking_talent', default=False )

    seeking_description = StringField(
        'seeking_description', validators=[Length(max=120)]
    )



class ArtistForm(Form):
    def validate_phone(form, field):
        phone_validator(field.data)

    def validate_genres(form, field):
        genres_validator(field.data)

    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=state_choices
    )
    phone = StringField(
        'phone', validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link', validators=[Optional(), URL(), Length(max=500)]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices = genres_choices
    )
    facebook_link = StringField(
        'facebook_link', validators=[Optional(), URL(), Length(max=120)]
    )

    website_link = StringField(
        'website_link', validators=[Optional(), URL(), Length(max=120)]
    )

    seeking_venue = BooleanField( 'seeking_venue' )

    seeking_description = StringField(
            'seeking_description', validators=[Optional(), Length(max=120)]
    )

