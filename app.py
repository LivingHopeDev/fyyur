#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from multiprocessing.dummy import Array
from pickle import TRUE
from re import A
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

# TODO: connect to a local postgresql database

app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    # instead of just date = dateutil.parser.parse(value)
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value

# def format_datetime(value, format='medium'):
#     date = dateutil.parser.parse(value)
#     if format == 'full':
#         format = "EEEE MMMM, d, y 'at' h:mma"
#     elif format == 'medium':
#         format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@ app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@ app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    # declaring up coming show function
    def upComingShow(start_time):
        return start_time > datetime.now()

    data = []

    # with_entities didn't give the intended result
    query = Venue.query.distinct(Venue.city, Venue.state).all()
    for output in query:
        result = {
            "city": output.city,
            "state": output.state
        }

        venues = Venue.query.filter_by(
            city=output.city, state=output.state).all()

        data2 = []
        for venue in venues:
            data2.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": str(Show.query.filter(upComingShow(Show.start_time)).filter(Show.venue_id == venue.id).count())
            })

        result["venues"] = data2

        data.append(result)

    return render_template('pages/venues.html', areas=data)


@ app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form.get('search_term', '')

    # declare an empty dict. and add the data
    response = {}
    response["count"] = Venue.query.filter(
        Venue.name.ilike(f'%{search_term}%')).count()

    response["data"] = Venue.query.filter(
        Venue.name.ilike(f'%{search_term}%')).all()

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    venue = Venue.query.get(venue_id)

    # do this when the venue_id entered isn't available in the database
    if not venue:
        return render_template('errors/404.html')

    # do this when the venue_id entered is available in the database

    def upComingShow(start_time):
        return start_time > datetime.now()

    def pastShow(start_time):
        return start_time < datetime.now()

    pastShows = []
    requestPastShows = Show.query.join(Artist).filter(
        Show.venue_id == venue_id).filter(pastShow(Show.start_time)).all()

    for show in requestPastShows:
        pastShows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time
        })

    upcomingShows = []
    requestUpcomingShows = Show.query.join(Artist).filter(
        Show.venue_id == venue_id).filter(upComingShow(Show.start_time)).all()

    for show in requestUpcomingShows:
        upcomingShows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time
        })

    data = {}
    data["id"] = venue.id
    data["name"] = venue.name
    data["genres"] = venue.genres.split(',')
    data["address"] = venue.address
    data["city"] = venue.city
    data["state"] = venue.state
    data["phone"] = venue.phone
    data["website"] = venue.website_link
    data["facebook_link"] = venue.facebook_link
    data["seeking_talent"] = venue.seeking_talent
    data["seeking_description"] = venue.seeking_description
    data["image_link"] = venue.image_link
    data["past_shows"] = pastShows
    data["upcoming_shows"] = upcomingShows
    data["past_shows_count"] = len(pastShows)
    data["upcoming_shows_count"] = len(upcomingShows)

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = VenueForm(request.form)

    try:

        venue = Venue(name=form.name.data,
                      city=form.city.data,
                      address=form.address.data,
                      state=form.state.data,
                      phone=form.phone.data,
                      genres=",".join(form.genres.data),
                      image_link=form.image_link.data,
                      facebook_link=form.facebook_link.data,
                      website_link=form.website_link.data,
                      seeking_talent=form.seeking_talent.data,
                      seeking_description=form.seeking_description.data)

        db.session.add(venue)
        db.session.commit()

        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] +
              ' was successfully listed!')
    except:
        # TODO: on unsuccessful db insert, flash an error instead.

        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
        print(sys.exec.info())
        print(form.errors)

        db.session.rollback()

    finally:
        db.session.close()
        return render_template('pages/home.html')


@ app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    venue = Venue.query.get(venue_id)

    error = False
    venue_name = venue.name
    try:
        db.session.delete(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash(f'An error occurred deleting venue {venue_name}.')
        print("Error in delete_venue()")
    else:
        flash(f'Successfully removed venue {venue_name}')
        return redirect(url_for('venues'))

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    # return None

#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists = Artist.query.all()
    data = artists

    return render_template('pages/artists.html', artists=data)


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get('search_term', '')

    response = {}
    response["count"] = Artist.query.filter(
        Artist.name.ilike(f'%{search_term}%')).count()

    response["data"] = Artist.query.filter(
        Artist.name.ilike(f'%{search_term}%')).all()

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    artist = Artist.query.get(artist_id)

   # do this when the artist_id entered isn't available in the database
    if not artist:
        return render_template('errors/404.html')

    # do this when the artist_id entered is available in the database

    def upComingShow(start_time):
        return start_time > datetime.now()

    def pastShow(start_time):
        return start_time < datetime.now()

    pastShows = []
    requestPastShows = Show.query.join(Artist).filter(
        Show.artist_id == artist_id).filter(pastShow(Show.start_time)).all()

    for show in requestPastShows:
        pastShows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time
        })

    upcomingShows = []
    requestUpcomingShows = Show.query.join(Artist).filter(
        Show.artist_id == artist_id).filter(upComingShow(Show.start_time)).all()

    for show in requestUpcomingShows:
        upcomingShows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time
        })

    data = {}
    data["id"] = artist.id
    data["name"] = artist.name
    data["genres"] = artist.genres.split(',')
    data["city"] = artist.city
    data["state"] = artist.state
    data["phone"] = artist.phone
    data["website"] = artist.website_link
    data["facebook_link"] = artist.facebook_link
    data["seeking_venue"] = artist.seeking_venue
    data["seeking_description"] = artist.seeking_description
    data["image_link"] = artist.image_link
    data["past_shows"] = pastShows
    data["upcoming_shows"] = upcomingShows
    data["past_shows_count"] = len(pastShows)
    data["upcoming_shows_count"] = len(upcomingShows)

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # TODO: populate form with fields from artist with ID <artist_id>

    form = ArtistForm()
    # artist_id = request.args.get('artist_id')
    artist = Artist.query.get(artist_id)

    data = {}
    data["name"] = artist.name
    data["genres"] = artist.genres.split(',')
    data["city"] = artist.city
    data["state"] = artist.state
    data["phone"] = artist.phone
    data["website"] = artist.website_link
    data["facebook_link"] = artist.facebook_link
    data["seeking_venue"] = artist.seeking_venue
    data["seeking_description"] = artist.seeking_description
    data["image_link"] = artist.image_link

    form.name.data = data["name"]
    form.city.data = data["city"]
    form.state.data = data["state"]
    form.phone.data = data["phone"]
    form.genres.data = data["genres"]
    form.facebook_link.data = data["facebook_link"]
    form.image_link.data = data["image_link"]
    form.website_link.data = data["website"]
    form.seeking_venue.data = data["seeking_venue"]
    form.seeking_description.data = data["seeking_description"]

    return render_template('forms/edit_artist.html', form=form, artist=data)


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    try:
        artist = Artist.query.get(artist_id)
        form = ArtistForm(request.form, obj=artist)
        if form.validate():
            form.populate_obj(artist)

            db.session.commit()
            flash('Artist ' + request.form['name'] +
                  ' was successfully updated!')
    except:
        db.session.rollback()
        flash('Update Artist ' +
              request.form['name'] + ' failed.')
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

    # TODO: populate form with values from venue with ID <venue_id>

    form = VenueForm()
    venue = Venue.query.get(venue_id)

    data = {}
    data["name"] = venue.name
    data["address"] = venue.address
    data["genres"] = venue.genres.split(',')
    data["city"] = venue.city
    data["state"] = venue.state
    data["phone"] = venue.phone
    data["website"] = venue.website_link
    data["facebook_link"] = venue.facebook_link
    data["seeking_talent"] = venue.seeking_talent
    data["seeking_description"] = venue.seeking_description
    data["image_link"] = venue.image_link

    form.name.data = data["name"]
    form.address.data = data["address"]
    form.city.data = data["city"]
    form.state.data = data["state"]
    form.phone.data = data["phone"]
    form.genres.data = data["genres"]
    form.facebook_link.data = data["facebook_link"]
    form.image_link.data = data["image_link"]
    form.website_link.data = data["website"]
    form.seeking_talent.data = data["seeking_talent"]
    form.seeking_description.data = data["seeking_description"]

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    try:
        venue = Venue.query.get(venue_id)
        form = VenueForm(request.form, obj=venue)
        if form.validate():
            form.populate_obj(venue)

            db.session.commit()
            flash('Venue ' + request.form['name'] +
                  ' was successfully updated!')
    except:
        db.session.rollback()
        flash('Update Venue ' +
              request.form['name'] + ' failed.')
    finally:
        db.session.rollback()
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():

    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = ArtistForm(request.form)
    try:

        artist = Artist(name=form.name.data,
                        city=form.city.data,
                        state=form.state.data,
                        phone=form.phone.data,
                        genres=",".join(form.genres.data),
                        image_link=form.image_link.data,
                        facebook_link=form.facebook_link.data,
                        website_link=form.website_link.data,
                        seeking_venue=form.seeking_venue.data,
                        seeking_description=form.seeking_description.data)

        db.session.add(artist)
        db.session.commit()

        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        # on unsuccessful db insert, flash an error instead.

        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')

        # print(sys.exec.info())
        # print(form.errors)

        db.session.rollback()

    finally:
        db.session.close()
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.

    shows = Show.query.order_by('start_time').all()
    data = []

    for show in shows:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.venue.id,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time

        })

    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    form = ShowForm(request.form)
    try:

        show = Show(artist_id=form.artist_id.data,
                    venue_id=form.venue_id.data,
                    start_time=form.start_time.data,
                    )
        db.session.add(show)
        db.session.commit()

        # on successful db insert, flash success
        flash('Show was successfully listed!')

    except:

        # on unsuccessful db insert, flash an error instead.
        flash('Show could not be listed.')

        print(sys.exec.info())
        print(form.errors)

        db.session.rollback()

    finally:
        db.session.close()
        return render_template('pages/home.html')

    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
